use serde::{Deserialize, Serialize};
use url::Url;
use uuid::Uuid;

use crate::site::{ChapterPage, MediaPage};

#[derive(Debug, Serialize, Deserialize)]
pub struct Site {
    pub id: Uuid,
    pub name: String,
    pub url: Url,

    pub media_page: MediaPage,
    pub chapter_page: ChapterPage,

    pub languages: Vec<String>,
    pub manga: Vec<String>,
}

impl Site {
    pub fn new(name: String, url: Url, media_page: MediaPage, chapter_page: ChapterPage) -> Self {
        Self {
            id: Uuid::new_v4(),
            name,
            url,
            media_page,
            chapter_page,
            languages: vec![],
            manga: vec![],
        }
    }

    pub fn get_media_page_url(&self, name_slug: &str) -> url::Url {
        self.media_page.get_url(&self.url, name_slug)
    }

    pub fn get_chapter_page_url(&self, name_slug: &str, num: isize) -> url::Url {
        self.chapter_page.get_url(&self.url, name_slug, num)
    }
}
