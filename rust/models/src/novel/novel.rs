use derive_more::{Deref, DerefMut};
use serde::{Deserialize, Serialize};

use crate::{
    media::{MediaMetadata, MediaTrait},
    novel::{Chapter, ChaptersRepo},
};

#[derive(Debug, Deref, DerefMut, Serialize, Deserialize)]
#[allow(dead_code)]
pub struct Novel {
    #[deref]
    #[deref_mut]
    pub metadata: MediaMetadata,
    #[serde(skip)]
    pub repo: Option<ChaptersRepo>,
}

impl Novel {
    pub fn new(metadata: MediaMetadata) -> Self {
        let repo = Some(ChaptersRepo::new(&metadata.folder));

        Self { metadata, repo }
    }

    pub fn add_chapter(&mut self, chapter: Chapter) -> Option<()> {
        match &mut self.repo {
            Some(repo) => {
                repo.insert(chapter);
                Some(())
            }
            None => None,
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
