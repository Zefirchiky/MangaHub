use std::{path::Path};

use handlers::JsonHandler;
use serde::{de::DeserializeOwned, Deserialize, Serialize};

use crate::chapter::ChapterTrait;


#[derive(Debug, Serialize, Deserialize)]
pub struct ChaptersRepoBase<T: ChapterTrait + Serialize> {
    #[serde(skip)]
    file_handler: JsonHandler,
    /// Chapters should always be avaliable between first and last, so they can be accessed by indexing.
    /// As chapters are dinamicaly scaled, better store in Box to avoid memory moves.
    chapters: Vec<T>,
    /// Aluxary chapters are chapters that may exist before real ones, and are not part of the story itself.
    aluxary_chapters: Vec<T>
}

impl<T: ChapterTrait + DeserializeOwned + Serialize> ChaptersRepoBase<T> {
    pub fn new(file: impl AsRef<Path>) -> Self {
        Self {
            file_handler: JsonHandler::new(file),
            chapters: vec![],
            aluxary_chapters: vec![],
        }
    }
    
    pub fn get(&self, i: isize) -> Option<&T> {
        if i >= 0 {
            self.chapters.get(i as usize)
        } else {
            self.aluxary_chapters.get((-i-1) as usize)
        }
    }
    
    pub fn get_mut(&mut self, i: isize) -> Option<&mut T> {
        if i >= 0 {
            self.chapters.get_mut(i as usize)
        } else {
            self.aluxary_chapters.get_mut((-i-1) as usize)
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

    pub fn load(&self) -> Result<Self, serde_json::Error> {
        self.file_handler.load::<Self>()
    }

    pub fn save(&self) -> Result<(), serde_json::Error> {
        self.file_handler.save(self)
    }
}


impl<T: ChapterTrait + Serialize> Drop for ChaptersRepoBase<T> {
    fn drop(&mut self) {
        if let Result::Err(err) = self.file_handler.save(self) {
            eprintln!("{err}");
        }
    }
}