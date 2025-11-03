use std::{fmt::Debug, io::{Read, Seek}};

use crate::{cache::CacheBase, image::Image};

pub struct Cache<R: Read + Seek> {
    cache: CacheBase<String, Image<R>>,
}

impl<R: Read + Seek> Debug for Cache<R> {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str("Image Cache")
    }
}

impl<R: Read + Seek> Default for Cache<R> {
    fn default() -> Self {
        Self {
            cache: CacheBase::new()
        }
    }
}

impl<R: Read + Seek> Cache<R> {
    pub fn new() -> Self {
        Self {
            cache: CacheBase::new()
        }
    }
}

impl<R: Read + Seek> std::ops::Deref for Cache<R> {
    type Target = CacheBase<String, Image<R>>;
    fn deref(&self) -> &Self::Target {
        &self.cache
    }
}

impl<R: Read + Seek> std::ops::DerefMut for Cache<R> {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.cache
    }
}