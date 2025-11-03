use std::{ops::{Deref, DerefMut}, path::Path};

use crate::{novel::Chapter, repos::ChaptersRepoBase};

#[derive(Debug)]
pub struct ChaptersRepo {
    repo: ChaptersRepoBase<Chapter>,
}

impl ChaptersRepo {
    pub fn new(file: impl AsRef<Path>) -> Self {
        Self {
            repo: ChaptersRepoBase::new(file)
        }
    }
}

impl Deref for ChaptersRepo {
    type Target = ChaptersRepoBase<Chapter>;

    fn deref(&self) -> &Self::Target {
        &self.repo
    }
}

impl DerefMut for ChaptersRepo {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.repo
    }
}