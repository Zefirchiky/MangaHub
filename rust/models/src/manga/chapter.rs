use std::io::Cursor;

use serde::{Deserialize, Serialize};

use crate::{chapter::{ChapterMetadata, ChapterTrait}, manga::Panel};

#[derive(Debug, Serialize, Deserialize)]
pub struct Chapter {
    pub metadata: ChapterMetadata,
    #[serde(skip)]
    pub images: crate::image::Cache<Cursor<bytes::Bytes>>,
    pub panels: Vec<Panel>,
}

impl Chapter {
    /// Creates a new `Chapter` with the given `metadata` and empty `image` and `panel` caches.
    pub fn new(metadata: ChapterMetadata) -> Self {
        Self {
            metadata,
            images: crate::image::Cache::new(),
            panels: vec![]
        }
    }
}

impl ChapterTrait for Chapter {
    fn metadata(&self) -> &ChapterMetadata {
        &self.metadata
    }
}