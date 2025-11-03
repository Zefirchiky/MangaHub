use crate::{manga::{Chapter, ChaptersRepo}, media::{MediaMetadata, MediaTrait}};

pub struct Manga {
    metadata: MediaMetadata,
    repo: Option<ChaptersRepo>
}

impl Manga {
    pub fn new(metadata: MediaMetadata) -> Self {
        let repo = Some(ChaptersRepo::new(&metadata.folder));

        Self {
            metadata,
            repo,
        }
    }
}

impl MediaTrait for Manga {
    fn metadata(&self) -> &MediaMetadata {
        &self.metadata
    }

    fn get_chapter(&self, num: isize) -> Option<&Chapter> {
        match &self.repo {
            Some(repo) => repo.get(num),
            None => None,
        }
    }
    
    fn get_chapter_mut(&mut self, num: isize) -> Option<&mut Chapter> {
        match &mut self.repo {
            Some(repo) => repo.get_mut(num),
            None => None,
        }
    }
}