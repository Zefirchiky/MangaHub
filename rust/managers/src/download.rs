use std::io::Cursor;

use crossbeam::channel::{Receiver, Sender};
use futures::StreamExt;
use image::{ImageFormat, ImageReader};
use log::warn;
use models::image::RamImage;
use reqwest::Client;
use tokio::task::JoinSet;
use url::Url;

pub enum ImageMessage {
    Metadata {
        i: usize,
        width: u32,
        height: u32,
        format: Option<ImageFormat>,
        size: Option<u64>,
    },
    Chunk {
        i: usize,
        chunk: bytes::Bytes,
    },
    Error {
        i: usize,
        err: reqwest::Error,
    },
    Complete {
        i: usize,
        bytes: bytes::Bytes,
    },
}

pub struct DownloadManager {
    client: Client,
    pub rt: tokio::runtime::Runtime,
}

impl DownloadManager {
    pub fn new() -> Self {
        Self {
            client: Client::default(),
            rt: tokio::runtime::Builder::new_multi_thread().build().unwrap(),
        }
    }

    fn download_once_blocking(url: Url) -> reqwest::Result<reqwest::blocking::Response> {
        Ok(reqwest::blocking::get(url)?.error_for_status()?)
    }

    async fn download_once_task(&self, url: Url) -> reqwest::Result<reqwest::Response> {
        Ok(self.client.get(url).send().await?.error_for_status()?)
    }

    fn download_and_send<T>(
        url: Url,
        tc: Sender<reqwest::Result<T>>,
        from_response: fn(reqwest::blocking::Response) -> reqwest::Result<T>,
    ) {
        if let Err(err) =
            tc.send(Self::download_once_blocking(url).and_then(|res| (from_response)(res)))
        {
            warn!(
                "Worker thread failed to send result: Receiver was dropped. Error: {:?}",
                err
            )
        }
    }

    /// Note: This function expect long-running program, so handle will not be returned
    pub fn download(url: Url) -> Receiver<reqwest::Result<bytes::Bytes>> {
        let (tc, rc) = crossbeam::channel::bounded(1);
        std::thread::spawn(move || Self::download_and_send(url, tc, |res| res.bytes()));
        rc
    }

    pub fn download_html(url: Url) -> Receiver<reqwest::Result<String>> {
        let (tc, rc) = crossbeam::channel::bounded(1);
        std::thread::spawn(move || Self::download_and_send(url, tc, |res| res.text()));
        rc
    }

    pub async fn download_html_task(&self, url: Url) -> reqwest::Result<String> {
        self.download_once_task(url).await?.text().await
    }

    pub fn download_image_channel(url: Url) -> Receiver<reqwest::Result<RamImage>> {
        let (tc, rc) = crossbeam::channel::bounded(1);
        std::thread::spawn(move || {
            Self::download_and_send(url, tc, |res| {
                let cursor = std::io::Cursor::new(res.bytes()?);
                let img = image::ImageReader::new(cursor)
                    .with_guessed_format()
                    .unwrap()
                    .into();
                Ok(img)
            })
        });
        rc
    }

    pub async fn download_image_task_channel(
        client: Client,
        tx: Sender<ImageMessage>,
        index: usize,
        url: Url,
    ) -> reqwest::Result<()> {
        let mut response = client.get(url).send().await?.error_for_status()?;
        let mut metadata_sent = false;
        let mut buffer = bytes::BytesMut::with_capacity(2048);

        while let Some(chunk) = response.chunk().await? {
            buffer.extend_from_slice(&chunk);
            if !metadata_sent {
                if buffer.len() >= 1024 {
                    if let Ok(reader) = ImageReader::new(Cursor::new(&buffer)).with_guessed_format()
                    {
                        let format = reader.format();
                        if let Ok((width, height)) = reader.into_dimensions() {
                            tx.send(ImageMessage::Metadata {
                                i: index,
                                width,
                                height,
                                format,
                                size: response.content_length(),
                            })
                            .unwrap();
                            metadata_sent = true;
                        }
                    }
                }
            }

            tx.send(ImageMessage::Chunk { i: index, chunk }).unwrap();
        }
        tx.send(ImageMessage::Complete {
            i: index,
            bytes: buffer.into(),
        })
        .unwrap();

        Ok(())
    }

    pub async fn download_image(
        client: Client,
        i: usize,
        url: Url,
    ) -> impl futures::Stream<Item = reqwest::Result<ImageMessage>> {
        let stream = async_stream::stream! {
            let mut response = client.get(url).send().await?.error_for_status()?;
            let mut metadata_sent = false;
            let mut buffer = bytes::BytesMut::with_capacity(2048);

            while let Some(chunk) = response.chunk().await? {
                buffer.extend_from_slice(&chunk);
                if !metadata_sent && buffer.len() >= 1024 {
                    if let Ok(reader) = ImageReader::new(Cursor::new(&buffer)).with_guessed_format() {
                        let format = reader.format();
                        if let Ok((width, height)) = reader.into_dimensions() {
                            yield Ok(ImageMessage::Metadata {
                                i,
                                width,
                                height,
                                format,
                                size: response.content_length(),
                            });
                            metadata_sent = true;
                        }
                    }
                }

                yield Ok(ImageMessage::Chunk { i, chunk })
            };

            yield Ok(ImageMessage::Complete { i, bytes: buffer.into() })
        };

        Box::pin(stream)
    }

    pub async fn download_images(
        &self,
        urls: Vec<Url>,
    ) -> impl futures::Stream<Item = ImageMessage> {
        let client = self.client.clone();
        Box::pin(async_stream::stream! {
            let mut downloads = futures::stream::iter(urls.into_iter().enumerate())
                .map(|(i, url)| {
                    let client = client.clone();
                    async move {
                        Self::download_image(client, i, url).await
                    }
                })
                .buffer_unordered(20);

            while let Some(mut image_stream) = downloads.next().await {
                while let Some(msg) = image_stream.next().await {
                    if let Ok(m) = msg {
                        yield m;
                    }
                }
            };
        })
    }

    /// Runs a given function in a new task with a bounded channel receiver.
    ///
    /// The function `f` should be an async function that takes a single argument of type `Sender<T>`.
    /// The function will be spawned in a new task and the channel receiver will be returned.
    ///
    /// The `cap` parameter specifies the buffer size of the channel receiver.
    /// If 0, the channel is unbounded.
    ///
    /// This is a convenience function for running a task in the background and communicating with it through a channel.
    ///
    /// # Example
    ///
    ///
    pub fn run_channels<F, T>(&self, f: F, cap: usize) -> Receiver<T>
    where
        F: AsyncFnOnce(Sender<T>) + Send + 'static,
        F::CallOnceFuture: Send + 'static,
    {
        let (tc, rc) = if cap > 0 {
            crossbeam::channel::bounded(cap)
        } else {
            crossbeam::channel::unbounded()
        };
        self.rt.spawn((f)(tc));
        rc
    }

    pub fn download_images_blocking(&self, urls: Vec<Url>) -> Receiver<ImageMessage> {
        // Vec<reqwest::Result<(usize, RamImage)>>
        let (tc, rc) = crossbeam::channel::bounded(urls.len());
        let client = self.client.clone();

        self.rt.spawn(async move {
            let mut set = JoinSet::new();

            for (i, url) in urls.into_iter().enumerate() {
                set.spawn(Self::download_image_task_channel(
                    client.clone(),
                    tc.clone(),
                    i,
                    url,
                ));
            }

            set.join_all().await;
        });

        rc
    }
}

#[cfg(test)]
mod test_download_manager {
    use std::time::Instant;

    // use models::{site::{ChapterPage, DataSource, Extractor, MediaPage, Site}, theme::Color};
    // use scraper::Html;
    use url::Url;
    // use uuid::Uuid;

    use crate::{DownloadManager, download::ImageMessage};

    #[test]
    fn image_downloading() {
        models::init();
        let start = Instant::now();
        let rc = DownloadManager::download_image_channel(Url::parse("https://asurascans.imagemanga.online/aHR0cHM6Ly9nZy5hc3VyYWNvbWljLm5ldC9zdG9yYWdlL21lZGlhLzM2ODU3Ni9jb252ZXJzaW9ucy8xMi1vcHRpbWl6ZWQud2VicA/aHR0cHM6Ly9hc3VyYWNvbWljLm5ldC9zZXJpZXMvbXlzdC1taWdodC1tYXloZW0tZGRhNzM3YjQ").expect("Wrong url"));
        println!("Started {:?}", start.elapsed());

        let img = rc.recv().unwrap().expect("Image was not parsed correctly");

        let file = handlers::file::File::new("test_images_download/test.webp");
        file.save(img.into_bytes()).unwrap();
        // file.save(img.compress_jxl()).expect("Was not saved successfully");
        println!("{:?}", start.elapsed())
    }

    #[test]
    fn images_downloading() {
        let start = Instant::now();
        let imgs = DownloadManager::new().download_images_blocking(vec![
            Url::parse("https://asurascans.imagemanga.online/aHR0cHM6Ly9nZy5hc3VyYWNvbWljLm5ldC9zdG9yYWdlL21lZGlhLzM2ODU3Ni9jb252ZXJzaW9ucy8xMi1vcHRpbWl6ZWQud2VicA/aHR0cHM6Ly9hc3VyYWNvbWljLm5ldC9zZXJpZXMvbXlzdC1taWdodC1tYXloZW0tZGRhNzM3YjQ").expect("Wrong url"),
            Url::parse("https://asurascans.imagemanga.online/aHR0cHM6Ly9nZy5hc3VyYWNvbWljLm5ldC9zdG9yYWdlL21lZGlhLzM2ODU3Ny9jb252ZXJzaW9ucy8xMy1vcHRpbWl6ZWQud2VicA/aHR0cHM6Ly9hc3VyYWNvbWljLm5ldC9zZXJpZXMvbXlzdC1taWdodC1tYXloZW0tZGRhNzM3YjQ").expect("Wrong url"),
            Url::parse("https://asurascans.imagemanga.online/aHR0cHM6Ly9nZy5hc3VyYWNvbWljLm5ldC9zdG9yYWdlL21lZGlhLzM2NzI4NS8wMi5qcGc/aHR0cHM6Ly9hc3VyYWNvbWljLm5ldC9zZXJpZXMvbXlzdC1taWdodC1tYXloZW0tZGRhNzM3YjQ").expect("Wrong url"),
            Url::parse("https://asurascans.imagemanga.online/aHR0cHM6Ly9nZy5hc3VyYWNvbWljLm5ldC9zdG9yYWdlL21lZGlhLzM2NzI4Ni8wMy5qcGc/aHR0cHM6Ly9hc3VyYWNvbWljLm5ldC9zZXJpZXMvbXlzdC1taWdodC1tYXloZW0tZGRhNzM3YjQ").expect("Wrong url"),
            Url::parse("https://asurascans.imagemanga.online/aHR0cHM6Ly9nZy5hc3VyYWNvbWljLm5ldC9zdG9yYWdlL21lZGlhLzM2NzI4Ny8wNC5qcGc/aHR0cHM6Ly9hc3VyYWNvbWljLm5ldC9zZXJpZXMvbXlzdC1taWdodC1tYXloZW0tZGRhNzM3YjQ").expect("Wrong url"),
            Url::parse("https://asurascans.imagemanga.online/aHR0cHM6Ly9nZy5hc3VyYWNvbWljLm5ldC9zdG9yYWdlL21lZGlhLzM2NzI4OC8wNS5qcGc/aHR0cHM6Ly9hc3VyYWNvbWljLm5ldC9zZXJpZXMvbXlzdC1taWdodC1tYXloZW0tZGRhNzM3YjQ").expect("Wrong url"),
        ]);

        for img in imgs {
            if let ImageMessage::Complete { i, bytes } = img {
                let file = handlers::file::File::new(format!("test_images_download/test{i}.webp"));
                file.save(bytes).expect("Was not saved successfully");
            }
        }
        println!("{:?}", start.elapsed())
    }

    // #[test]
    // fn html() {
    //     ffi::init();
    //     let mut sites_manager = SitesManager::new("test_full/test.json");
    //     sites_manager.load();

    //     for (id, site) in sites_manager.repo.iter() {
    //         log::info!("{id} {}", site.name)
    //     }
    //     // let site = Site::new(
    //     //     "AsuraScans".to_string(),
    //     //     Url::parse("https://asurascanz.com").unwrap(),
    //     //     MediaPage::new(
    //     //         "manga/{slug}".to_string(),
    //     //         Some(Extractor::new("div#titlemove h1.entry-title", DataSource::Text(0))),
    //     //         Some(Extractor::new("div.thumb img", DataSource::Attr("src".to_string()))),
    //     //         Some(Extractor::new("span.chapternum", DataSource::Text(0))),
    //     //     ),
    //     //     ChapterPage::new(
    //     //         "{slug}-chapter-{num}".to_string(),
    //     //         None,
    //     //         Some(Extractor::new("div#readerarea p img.lazyload", DataSource::Attr("data-src".to_string()))),
    //     //         None
    //     //     ),
    //     // );
    //     // let id = sites_manager.add(site);
    //     let site = sites_manager.repo.get_by_name("AsuraScans").unwrap();

    //     let html = sites_manager
    //         .download_chapter_content_blocking(
    //             [site.id].to_vec(),
    //             "myst-might-mayhem".to_string(),
    //             94,
    //         )
    //         .unwrap();
    //     if let Some(urls) = html.image_urls {
    //         let rc = DownloadManager::new().download_images_blocking(urls);
    //         for message in rc {
    //             if let ImageMessage::Complete { i, bytes } = message {
    //                 let image_f = handlers::file::File::new(format!("test_full/{i}.webp"));
    //                 image_f.save(bytes).unwrap();
    //             }
    //         }
    //     }
    //     sites_manager.save();
    //     // dbg!(el);
    // }
}
