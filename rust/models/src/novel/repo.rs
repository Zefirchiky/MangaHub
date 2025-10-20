use std::{path::{Path, PathBuf}};

use crate::novel::ChapterTrait;

pub struct ChaptersRepo<T: ChapterTrait> {
    _path: PathBuf,
    /// Chapters should always be avaliable between first and last, so they can be accessed by indexing.
    /// As chapters are dinamicaly scaled, better store in Box to avoid memory moves.
    chapters: Vec<T>,
    /// Aluxary chapters are chapters that may exist before real ones, and are not part of the story itself.
    aluxary_chapters: Vec<T>
}

impl<T: ChapterTrait> ChaptersRepo<T> {
    pub fn new(path: impl AsRef<Path>) -> Self {
        Self {
            _path: path.as_ref().to_path_buf(),
            chapters: Vec::new(),
            aluxary_chapters: Vec::new(),
        }
    }

    pub fn get(&self, i: i32) -> Option<&T> {
        if i >= 0 {
            self.chapters.get(i as usize)
        } else {
            self.aluxary_chapters.get((-i-1) as usize)
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
}