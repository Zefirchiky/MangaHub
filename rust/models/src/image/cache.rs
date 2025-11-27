use std::io::{Read, Seek};

use derive_more::{Debug, Deref, DerefMut, From};

use crate::{cache::CacheBase, image::Image};

#[derive(Debug, Deref, DerefMut, From)]
pub struct Cache<R: Read + Seek> {
    cache: CacheBase<String, Image<R>>,
}

impl<R: Read + Seek> Default for Cache<R> {
    fn default() -> Self {
        Self {
            cache: CacheBase::new(),
        }
    }
}

impl<R: Read + Seek> Cache<R> {
    pub fn new() -> Self {
        Self {
            cache: CacheBase::new(),
        }
    }
}
