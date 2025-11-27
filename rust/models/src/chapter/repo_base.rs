use handlers::file::{Dir, ModelFileTrait};
use serde::{Deserialize, Serialize, de::DeserializeOwned};

use crate::chapter::ChapterTrait;

pub trait ChapterIoTrait {
    fn save(&self, dir: &Dir);
    fn load(&mut self, dir: &Dir);
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RepoBase<C: ChapterTrait + ChapterIoTrait + Serialize, F: ModelFileTrait> {
    #[serde(skip)]
    dir: Dir,
    #[serde(skip)]
    file: F,
    /// Chapters should always be available between first and last, so they can be accessed by indexing.
    /// As chapters are dynamically scaled, better store in Box to avoid memory moves.
    chapters: Vec<C>,
    /// Appendix chapters are chapters that may exist before real ones, and are not part of the story itself.
    appendix_chapters: Vec<C>,
}

impl<C: ChapterTrait + ChapterIoTrait + DeserializeOwned + Serialize, F: ModelFileTrait> RepoBase<C, F> {
    pub fn new(dir: Dir, file: F) -> Self {
        Self {
            dir,
            file,
            chapters: vec![],
            appendix_chapters: vec![],
        }
    }

    pub fn get(&self, i: isize) -> Option<&C> {
        if i > 0 {
            self.chapters.get((i - 1) as usize)
        } else {
            self.appendix_chapters.get(-i as usize)
        }
    }

    pub fn get_mut(&mut self, i: isize) -> Option<&mut C> {
        if i > 0 {
            self.chapters.get_mut((i - 1) as usize)
        } else {
            self.appendix_chapters.get_mut(-i as usize)
        }
    }

    pub fn get_all(&self) -> Vec<&C> {
        let mut res = Vec::with_capacity(self.appendix_chapters.len() + self.chapters.len());
        res.extend(self.appendix_chapters.iter().rev().collect::<Vec<&C>>());
        res.extend(self.chapters.iter().collect::<Vec<&C>>());
        res
    }

    pub fn get_all_mut(&mut self) -> Vec<&mut C> {
        let mut res = Vec::with_capacity(self.appendix_chapters.len() + self.chapters.len());
        res.extend(self.appendix_chapters.iter_mut().rev().collect::<Vec<&mut C>>());
        res.extend(self.chapters.iter_mut().collect::<Vec<&mut C>>());
        res
    }

    pub fn insert(&mut self, chapter: C) {
        let num = chapter.metadata().num;
        if num > 0 {
            // ? Real chapters start at 1
            self.chapters.insert((num - 1) as usize, chapter)
        } else {
            self.appendix_chapters.insert(-num as usize, chapter);
        }
    }

    fn get_chapter_folder_name(chap: &C) -> String {
        format!("chapter_{}_{}", chap.metadata().num, chap.metadata().name)
    }

    pub fn save(&self) -> Result<(), <F as ModelFileTrait>::Error> {
        for chap in self.get_all() {
            chap.save(&self.dir.join(&Self::get_chapter_folder_name(chap)).into());
        }
        self.file.save_model(self)
    }
    
    pub fn load(&mut self) -> Result<(), <F as ModelFileTrait>::Error> {
        let new = self.file.load_model::<Self>()?;
        self.appendix_chapters = new.appendix_chapters;
        self.chapters = new.chapters;
        let dir = self.dir.clone();
        for chap in self.get_all_mut() {
            chap.load(&dir.join(&Self::get_chapter_folder_name(chap)).into());
        }
        Ok(())
    }
}
