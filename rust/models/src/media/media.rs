use std::path::PathBuf;

use chrono::Datelike;
use indexmap::IndexSet;
use serde::{Deserialize, Serialize, de::DeserializeOwned};
use uuid::Uuid;

use crate::chapter::ChapterTrait;

#[allow(dead_code)]
#[derive(Debug, Serialize, Deserialize)]
pub enum Status {
    Abandoned,
    Paused,
    Ongoing,
    Finished,
}

#[allow(dead_code)]
#[derive(Debug, Serialize, Deserialize)]
pub enum CoverStatus {
    Exist,
    Downloading,
    None,
}

pub trait MediaTrait: Serialize + DeserializeOwned {
    fn metadata(&self) -> &MediaMetadata;

    fn get_chapter(&self, num: isize) -> Option<&impl ChapterTrait>;
    fn get_chapter_mut(&mut self, num: isize) -> Option<&mut impl ChapterTrait>;
}

#[allow(dead_code)]
#[derive(Debug, Serialize, Deserialize)]
pub struct MediaMetadata {
    pub name: String,
    pub slug: String,
    pub id: Uuid,
    pub folder: PathBuf,
    pub description: String,
    pub author: String,
    pub status: Status,

    pub cover: CoverStatus,

    pub year: u32,
    // last_updated: str = Field(default_factory=lambda: str(datetime.now))
    pub sites: Vec<Uuid>,

    pub current_chapter: i32,
    pub last_read_chapter: i32,
    pub checked_chapters: IndexSet<i32>,
}

impl MediaMetadata {
    pub fn new(name: String, folder: String) -> Self {
        let name_slug = slug::slugify(&name);
        let folder = PathBuf::from(folder).join(&name_slug);

        Self {
            name,
            slug: name_slug,
            id: Uuid::new_v4(),
            folder,
            description: String::new(),
            author: String::new(),
            status: Status::Ongoing,
            cover: CoverStatus::None,
            year: chrono::Utc::now().year() as u32,
            sites: vec![],
            current_chapter: i32::MIN,
            last_read_chapter: i32::MIN,
            checked_chapters: IndexSet::new(),
        }
    }
}
