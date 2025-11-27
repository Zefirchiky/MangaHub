use std::{sync::Arc};

use crossbeam::channel::Sender;
use futures::StreamExt;
use handlers::file::{Json, ModelJsonIoError};
use models::{
    manga::{Chapter, Manga, Repo},
    media::MediaMetadata,
};
use uuid::Uuid;

use crate::{DownloadManager, ImageMessage, SitesManager};

pub struct MangaManager {
    pub repo: Repo,
    pub sites_manager: Arc<SitesManager>,
    pub download_manager: Arc<DownloadManager>,
}

impl MangaManager {
    pub fn new(
        file: Json,
        sites_manager: Arc<SitesManager>,
        download_manager: Arc<DownloadManager>,
    ) -> Self {
        Self {
            repo: Repo::new(file),
            sites_manager,
            download_manager,
        }
    }

    pub fn new_manga(&mut self, name: String) -> Uuid {
        let manga = Manga::new(MediaMetadata::new(name, self.repo.file.file.parent().unwrap().into()));
        manga.id
    }

    /// Downloads all images of a given chapter.
    ///
    /// This function is blocking and should be called in another thread.
    ///
    /// If the chapter does not have image urls set, it will download the chapter content
    /// and set the image urls.
    ///
    /// Returns a receiver of `ImageMessage`s if successful, otherwise `None`.
    ///
    /// # Arguments
    ///
    /// * `manga`: The manga to download images from
    /// * `chapter`: The chapter to download images from
    ///
    /// # Errors
    ///
    /// If the chapter content download fails, `None` is returned.
    pub fn download_chapter_images(
        &self,
        manga: &Manga,
        chapter: &Chapter,
    ) -> Option<crossbeam::channel::Receiver<ImageMessage>> {
        // let (tc, rc) = crossbeam::channel::unbounded();
        let download_manager = Arc::clone(&self.download_manager);
        if let Some(urls) = chapter.image_urls.clone() {
            let len = urls.len();
            return Some(self.download_manager.run_channels(
                |tc: Sender<ImageMessage>| async move {
                    while let Some(msg) = download_manager
                        .download_images(urls.clone())
                        .await
                        .next()
                        .await
                    {
                        tc.send(msg).unwrap();
                    }
                },
                len,
            ));
        }

        let name_slug = manga.slug.clone();
        let sites = manga.sites.clone();
        let sites_manager = Arc::clone(&self.sites_manager);
        let image_urls = chapter.image_urls.clone();
        let chapter_num = chapter.num;
        let download_manager = Arc::clone(&self.download_manager);
        let rc = self.download_manager.run_channels(
            async move |tc: Sender<ImageMessage>| {
                dbg!("Here");
                let chapter_image_urls = match image_urls {
                    Some(urls) => urls,
                    None => {
                        dbg!("Here 2");
                        let chapter_content = match sites_manager
                            .clone()
                            .download_chapter_content(sites, name_slug, chapter_num)
                            .await
                        {
                            Some(cont) => cont,
                            None => return,
                        };
                        dbg!("Here 3");
                        // {
                        //     let mut mut_chap = chapter_mut.write().await;
                        //     Self::fill_chapter_with_content(&mut mut_chap, chapter_content); // TODO: Cache the urls and fill other fields
                        // }
                        match chapter_content.image_urls.clone() {
                            Some(urls) => urls,
                            None => return,
                        }
                    }
                };

                while let Some(msg) = download_manager
                    .download_images(chapter_image_urls.clone())
                    .await
                    .next()
                    .await
                {
                    tc.send(msg).unwrap();
                }
            },
            0,
        );
        Some(rc)
    }

    // fn fill_chapter_with_content(chapter: &mut Chapter, content: ChapterPageContent) {
    //     if let Some(urls) = content.image_urls {
    //         chapter.image_urls = Some(urls);
    //     }
    //     if let Some(name) = content.name {
    //         chapter.name = name;
    //     }
    // }

    pub fn save(&self) -> Result<(), ModelJsonIoError> {
        self.repo.save()
    }

    pub fn load(&mut self) -> Result<(), ModelJsonIoError> {
        self.repo.load()
    }
}

#[cfg(test)]
mod manga_manager_test {}
