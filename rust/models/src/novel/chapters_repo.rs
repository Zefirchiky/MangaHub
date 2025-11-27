use handlers::file::Json;

use crate::{chapter::{ChapterIoTrait, RepoBase}, novel::Chapter};

impl ChapterIoTrait for Chapter {
    fn save(&self, _dir: &handlers::file::Dir) {
        todo!();
    }

    fn load(&mut self, _dir: &handlers::file::Dir) {
        todo!();
    }
}

pub type ChaptersRepo = RepoBase<Chapter, Json>;
