use std::io::Cursor;

use derive_more::{Debug, Deref, DerefMut, From};
use serde::{Deserialize, Serialize};
use url::Url;

use crate::{
    chapter::{ChapterMetadata, ChapterTrait},
    manga::Panel,
};

#[derive(Debug, From, Deref, DerefMut, Serialize, Deserialize)]
pub struct Chapter {
    #[deref]
    #[deref_mut]
    pub metadata: ChapterMetadata,
    #[serde(skip)]
    #[debug(skip)]
    pub images: crate::image::Cache<Cursor<bytes::Bytes>>,
    pub image_urls: Option<Vec<Url>>,
    pub panels: Vec<Panel>,
}

impl Chapter {
    /// Creates a new `Chapter` with the given `metadata` and empty `image` and `panel` caches.
    pub fn new(metadata: ChapterMetadata) -> Self {
        Self {
            metadata,
            images: crate::image::Cache::new(),
            image_urls: None,
            panels: vec![],
        }
    }
}

impl ChapterTrait for Chapter {
    fn metadata(&self) -> &ChapterMetadata {
        &self.metadata
    }
}