use std::path::PathBuf;

use chrono::Datelike;
use indexmap::IndexSet;

use crate::novel::{NovelChapter, ChaptersRepo};


#[allow(dead_code)]
pub enum MediaStatus {
    Abandoned,
    Paused,
    Ongoing,
    Finished,
}

#[allow(dead_code)]
pub enum MediaCoverStatus {
    Exist,
    Downloading,
    None,
}

#[allow(dead_code)]
pub struct Novel {
    name: String,
    id: String,
    folder: PathBuf,
    description: String = String::new(),
    author: String = String::new(),
    status: MediaStatus = MediaStatus::Ongoing,

    cover: MediaCoverStatus = MediaCoverStatus::None,

    year: u32,
    // last_updated: str = Field(default_factory=lambda: str(datetime.now))

    // sites: list[str] = ["MangaDex"],
    sites: Vec<String>,

    current_chapter: i32 = i32::MIN,
    last_read_chapter: i32 = i32::MIN,
    checked_chapters: IndexSet<i32>,

    repo: ChaptersRepo<NovelChapter>,
}

impl Novel {
    pub fn new(name: String, folder: String) -> Self {
        let id = Self::id_from_name(&name);
        let folder = PathBuf::from(folder);
        let repo = ChaptersRepo::new(folder.join(&id));

        Self {
            name,
            id: id,
            folder: folder,
            description: String::new(),
            author: String::new(),
            status: MediaStatus::Ongoing,
            cover: MediaCoverStatus::None,
            year: chrono::Utc::now().year() as u32,
            sites: vec!["MangaDex".to_string()],
            current_chapter: -1,
            last_read_chapter: -1,
            checked_chapters: IndexSet::new(),
            repo,
        }
    }

    pub fn id_from_name(name: &String) -> String {
        name.to_lowercase().replace(' ', "_")
    }
}