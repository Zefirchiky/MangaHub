use std::path::PathBuf;

use chrono::Datelike;
use indexmap::IndexSet;
use serde::{Deserialize, Serialize};

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

pub trait MediaTrait {
    fn metadata(&self) -> &MediaMetadata;

    fn get_chapter(&self, num: isize) -> Option<&impl ChapterTrait>;
    fn get_chapter_mut(&mut self, num: isize) -> Option<&mut impl ChapterTrait>;
}

#[allow(dead_code)]
#[derive(Debug, Serialize, Deserialize)]
pub struct MediaMetadata {
    pub name: String,
    pub id: String,
    pub folder: PathBuf,
    pub description: String,
    pub author: String,
    pub status: Status,

    pub cover: CoverStatus,

    pub year: u32,
    // last_updated: str = Field(default_factory=lambda: str(datetime.now))

    pub sites: Vec<String>,

    pub current_chapter: i32,
    pub last_read_chapter: i32,
    pub checked_chapters: IndexSet<i32>,
}

impl MediaMetadata {
    pub fn new(name: String, folder: String) -> Self {
        let id = Self::id_from_name(&name);
        let folder = PathBuf::from(folder).join(&id);

        Self {
            name,
            id,
            folder,
            description: String::new(),
            author: String::new(),
            status: Status::Ongoing,
            cover: CoverStatus::None,
            year: chrono::Utc::now().year() as u32,
            sites: vec!["MangaDex".to_string()],
            current_chapter: i32::MIN,
            last_read_chapter: i32::MIN,
            checked_chapters: IndexSet::new(),
        }
    }

    pub fn id_from_name(name: &String) -> String {
        name.to_lowercase().replace(' ', "_")
    }
}