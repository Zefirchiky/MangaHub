use handlers::file::Dir;
use log::{info, warn};
use models::site::{ChapterPageContent, Repo, Site};
use scraper::Html;
use uuid::Uuid;

use crate::DownloadManager;

pub struct SitesManager {
    pub repo: Repo,
}

impl SitesManager {
    pub fn new(dir: Dir) -> Self {
        Self {
            repo: Repo::new(dir),
        }
    }

    pub fn add(&mut self, site: Site) -> Uuid {
        // Uuid is used, never fails
        let id = site.id;
        self.repo.insert(id, site);
        id
    }

    /// Downloads a chapter page from a given list of sites
    ///
    /// Returns an `Html` object if the download is successful, otherwise `None`
    ///
    /// # Arguments
    ///
    /// * `sites`: A list of site IDs to download from
    /// * `name_slug`: The name slug of the manga
    /// * `num`: The chapter number to download
    ///
    /// # Errors
    ///
    /// If a site is not found, a warning is logged.
    /// If the download fails, a warning is logged with the error message.
    pub fn download_chapter_page(site: &Site, name_slug: &str, num: isize) -> Option<Html> {
        let chap_url = site.chapter_page.get_url(&site.url, name_slug, num);
        let text = match DownloadManager::download_html(chap_url)
            .recv()
            .expect("Failed to receive a text")
        {
            Ok(t) => t,
            Err(err) => {
                warn!(
                    "Failed to download chapter page of `{name_slug}` {num} from site `{}` ({}): {err:#?}",
                    site.name, site.id
                );
                return None;
            }
        };

        Some(scraper::Html::parse_document(&text))
    }

    pub async fn download_chapter_page_task(
        site: &Site,
        name_slug: &str,
        num: isize,
    ) -> Option<Html> {
        let chap_url = site.chapter_page.get_url(&site.url, name_slug, num);
        let text = match DownloadManager::new().download_html_task(chap_url).await {
            Ok(t) => t,
            Err(err) => {
                warn!(
                    "Failed to download chapter page of `{name_slug}` {num} from site `{}` ({}): {err:#?}",
                    site.name, site.id
                );
                return None;
            }
        };

        Some(scraper::Html::parse_document(&text))
    }

    pub fn download_chapter_content_blocking(
        &self,
        sites: Vec<Uuid>,
        name_slug: String,
        num: isize,
    ) -> Option<ChapterPageContent> {
        for site_id in sites {
            let site = match self.repo.get(&site_id) {
                Some(s) => s,
                None => {
                    warn!("Site with id {site_id} was not found");
                    continue;
                }
            };

            let html = Self::download_chapter_page(site, &name_slug, num)?;
            return Some(site.chapter_page.parse_html(&html));
        }

        None
    }

    pub async fn download_chapter_content(
        &self,
        sites: Vec<Uuid>,
        name_slug: String,
        num: isize,
    ) -> Option<ChapterPageContent> {
        for site_id in sites {
            let site = match self.repo.get(&site_id) {
                Some(s) => s,
                None => {
                    warn!("Site with id {site_id} was not found");
                    continue;
                }
            };

            let html = Self::download_chapter_page_task(site, &name_slug, num).await?;
            return Some(site.chapter_page.parse_html(&html));
        }

        None
    }

    pub fn parse_chapter_html(site: Site, html: Html) -> ChapterPageContent {
        site.chapter_page.parse_html(&html)
    }

    pub fn load(&mut self) {
        match self.repo.load() {
            Ok(_) => info!("SitesManager was loaded successfully"),
            Err(err) => warn!("SitesManager failed to load: {err}")
        }
    }
    
    pub fn save(&self) {
        match self.repo.save() {
            Ok(_) => info!("SitesManager was saved successfully"),
            Err(err) => warn!("SitesManager failed to save: {err}")
        }
    }
}
