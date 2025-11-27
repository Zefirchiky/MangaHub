use chrono::Datelike;
use handlers::file::Dir;
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
    pub dir: Dir,
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
    /// Creates a new `MediaMetadata` instance from a given name and directory path.
    ///
    /// The name slug is generated from the given name using the `slug` crate.
    /// The directory path is joined with the name slug to ensure that the media's
    /// metadata is stored in a unique directory.
    ///
    /// The `year` field is set to the current year.
    ///
    /// All other fields are set to their default values.
    pub fn new(name: String, dir: Dir) -> Self {
        let name_slug = slug::slugify(&name);
        let dir = dir.join(&name_slug).into();

        Self {
            name,
            slug: name_slug,
            id: Uuid::new_v4(),
            dir,
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
