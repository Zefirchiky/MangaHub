use std::path::Path;

use handlers::file::{Json, ModelFileTrait, ModelJsonIoError};
use serde::{Deserialize, Serialize, de::DeserializeOwned};

use crate::chapter::ChapterTrait;

#[derive(Debug, Serialize, Deserialize)]
pub struct RepoBase<T: ChapterTrait + Serialize> {
    #[serde(skip)]
    file_handler: Json,
    /// Chapters should always be avaliable between first and last, so they can be accessed by indexing.
    /// As chapters are dinamicaly scaled, better store in Box to avoid memory moves.
    chapters: Vec<T>,
    /// Aluxary chapters are chapters that may exist before real ones, and are not part of the story itself.
    aluxary_chapters: Vec<T>,
}

impl<T: ChapterTrait + DeserializeOwned + Serialize> RepoBase<T> {
    pub fn new(file: impl AsRef<Path>) -> Self {
        Self {
            file_handler: Json::new(file),
            chapters: vec![],
            aluxary_chapters: vec![],
        }
    }

    pub fn get(&self, i: isize) -> Option<&T> {
        if i >= 0 {
            self.chapters.get(i as usize)
        } else {
            self.aluxary_chapters.get((-i - 1) as usize)
        }
    }

    pub fn get_mut(&mut self, i: isize) -> Option<&mut T> {
        if i >= 0 {
            self.chapters.get_mut(i as usize)
        } else {
            self.aluxary_chapters.get_mut((-i - 1) as usize)
        }
    }

    pub fn insert(&mut self, chapter: T) {
        let num = chapter.metadata().num;
        if num >= 0 {
            self.chapters.insert(num as usize, chapter)
        } else {
            self.aluxary_chapters.insert((-num - 1) as usize, chapter);
        }
    }

    pub fn load(&self) -> Result<Self, ModelJsonIoError> {
        self.file_handler.load_model::<Self>()
    }

    pub fn save(&self) -> Result<(), ModelJsonIoError> {
        self.file_handler.save_model(self)
    }
}