use derive_more::{Deref, DerefMut, From};
use serde::{Deserialize, Serialize};

use crate::{
    manga::{Chapter, ChaptersRepo},
    media::{MediaMetadata, MediaTrait},
};

#[derive(Debug, From, Deref, DerefMut, Serialize, Deserialize)]
pub struct Manga {
    #[deref]
    #[deref_mut]
    metadata: MediaMetadata,
    #[serde(skip)]
    repo: Option<ChaptersRepo>,
}

impl Manga {
    pub fn new(metadata: MediaMetadata) -> Self {
        let repo = Some(ChaptersRepo::new(&metadata.folder));

        Self { metadata, repo }
    }

    pub fn insert_chapter(&mut self, chapter: Chapter) -> Option<()> {
        match &mut self.repo {
            Some(repo) => {
                repo.insert(chapter);
                Some(())
            }
            None => None,
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