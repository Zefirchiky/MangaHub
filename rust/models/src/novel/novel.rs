use serde::{Deserialize, Serialize};

use crate::{media::{MediaMetadata, MediaTrait}, novel::{Chapter, ChaptersRepo}};

#[allow(dead_code)]
#[derive(Debug, Serialize, Deserialize)]
pub struct Novel {
    metadata: MediaMetadata,
    #[serde(skip)]
    repo: Option<ChaptersRepo>,
}

impl Novel {
    pub fn new(metadata: MediaMetadata) -> Self {
        let repo = Some(ChaptersRepo::new(&metadata.folder));

        Self {
            metadata,
            repo,
        }
    }
}

impl MediaTrait for Novel {
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