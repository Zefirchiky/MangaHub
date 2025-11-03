use serde::{Deserialize, Serialize};

use crate::{chapter::{ChapterMetadata, ChapterTrait}, manga::Image};

#[derive(Debug, Serialize, Deserialize)]
pub struct Chapter {
    metadata: ChapterMetadata,
    images: Vec<Image>,
}

impl Chapter {
    pub fn new(metadata: ChapterMetadata) -> Self {
        Self {
            metadata,
            images: vec![]
        }
    }
}

impl ChapterTrait for Chapter {
    fn metadata(&self) -> &ChapterMetadata {
        &self.metadata
    }
}