use models::image::RamImage;
use reqwest::Client;
use tokio::{task::JoinSet};
use url::Url;

pub struct DownloadManager {
    client: Client,
}

impl DownloadManager {
    pub fn new() -> Self {
        Self {
            client: Client::new()
        }
    }

    pub fn download_image(url: Url) -> reqwest::Result<RamImage> {
        let response = reqwest::blocking::get(url)?.error_for_status()?;
        let bytes = response.bytes()?;
        let cursor = std::io::Cursor::new(bytes);
        reqwest::Result::Ok(image::ImageReader::new(cursor).with_guessed_format().unwrap().into())
    }

    pub async fn download_image_task(client: Client, url: Url) -> reqwest::Result<RamImage> {
        let response = client.get(url).send().await?
            .error_for_status()?;
        
        let bytes = response.bytes().await?;
        let cursor = std::io::Cursor::new(bytes);
        reqwest::Result::Ok(image::ImageReader::new(cursor).with_guessed_format().unwrap().into())
    }

    pub fn download_images(&self, urls: Vec<Url>) -> Vec<reqwest::Result<RamImage>> {
        let rt = tokio::runtime::Runtime::new().expect("Failed to start runtime");

        rt.block_on(async {
            let mut set = JoinSet::new();

            for url in urls {
                set.spawn(
                    Self::download_image_task(self.client.clone(), url)
                );
            }
            
            set.join_all().await
        })
    }
}


#[cfg(test)]
mod test_download_manager {
    use std::time::Instant;

    use url::Url;

    use crate::DownloadManager;

    #[test]
    fn image_downloading() {
        models::init();
        let start = Instant::now();
        let img = DownloadManager::download_image(Url::parse("https://asurascans.imagemanga.online/aHR0cHM6Ly9nZy5hc3VyYWNvbWljLm5ldC9zdG9yYWdlL21lZGlhLzM2ODU3Ni9jb252ZXJzaW9ucy8xMi1vcHRpbWl6ZWQud2VicA/aHR0cHM6Ly9hc3VyYWNvbWljLm5ldC9zZXJpZXMvbXlzdC1taWdodC1tYXloZW0tZGRhNzM3YjQ").expect("Wrong url"))
        .unwrap();

        let file = handlers::FileHandler::new("test/test.webp");
        file.save(img.compress_jxl()).expect("Was not saved succesfully");
        println!("{:?}", start.elapsed())
    }
    
    #[test]
    fn images_downloading() {
        let start = Instant::now();
        let imgs = DownloadManager::new().download_images(vec![
            Url::parse("https://asurascans.imagemanga.online/aHR0cHM6Ly9nZy5hc3VyYWNvbWljLm5ldC9zdG9yYWdlL21lZGlhLzM2ODU3Ni9jb252ZXJzaW9ucy8xMi1vcHRpbWl6ZWQud2VicA/aHR0cHM6Ly9hc3VyYWNvbWljLm5ldC9zZXJpZXMvbXlzdC1taWdodC1tYXloZW0tZGRhNzM3YjQ").expect("Wrong url"),
            Url::parse("https://asurascans.imagemanga.online/aHR0cHM6Ly9nZy5hc3VyYWNvbWljLm5ldC9zdG9yYWdlL21lZGlhLzM2ODU3Ny9jb252ZXJzaW9ucy8xMy1vcHRpbWl6ZWQud2VicA/aHR0cHM6Ly9hc3VyYWNvbWljLm5ldC9zZXJpZXMvbXlzdC1taWdodC1tYXloZW0tZGRhNzM3YjQ").expect("Wrong url"),
            Url::parse("https://asurascans.imagemanga.online/aHR0cHM6Ly9nZy5hc3VyYWNvbWljLm5ldC9zdG9yYWdlL21lZGlhLzM2NzI4NS8wMi5qcGc/aHR0cHM6Ly9hc3VyYWNvbWljLm5ldC9zZXJpZXMvbXlzdC1taWdodC1tYXloZW0tZGRhNzM3YjQ").expect("Wrong url"),
            Url::parse("https://asurascans.imagemanga.online/aHR0cHM6Ly9nZy5hc3VyYWNvbWljLm5ldC9zdG9yYWdlL21lZGlhLzM2NzI4Ni8wMy5qcGc/aHR0cHM6Ly9hc3VyYWNvbWljLm5ldC9zZXJpZXMvbXlzdC1taWdodC1tYXloZW0tZGRhNzM3YjQ").expect("Wrong url"),
            Url::parse("https://asurascans.imagemanga.online/aHR0cHM6Ly9nZy5hc3VyYWNvbWljLm5ldC9zdG9yYWdlL21lZGlhLzM2NzI4Ny8wNC5qcGc/aHR0cHM6Ly9hc3VyYWNvbWljLm5ldC9zZXJpZXMvbXlzdC1taWdodC1tYXloZW0tZGRhNzM3YjQ").expect("Wrong url"),
            Url::parse("https://asurascans.imagemanga.online/aHR0cHM6Ly9nZy5hc3VyYWNvbWljLm5ldC9zdG9yYWdlL21lZGlhLzM2NzI4OC8wNS5qcGc/aHR0cHM6Ly9hc3VyYWNvbWljLm5ldC9zZXJpZXMvbXlzdC1taWdodC1tYXloZW0tZGRhNzM3YjQ").expect("Wrong url"),
        ]);

        for (i, img) in imgs.into_iter().enumerate() {
            let img = img.unwrap();
            let file = handlers::FileHandler::new(format!("test/test{i}.webp"));
            file.save(img.into_bytes()).expect("Was not saved succesfully");
        }
        println!("{:?}", start.elapsed())
    }
}