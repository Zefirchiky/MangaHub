use std::sync::Arc;

use handlers::file::File;
use models::{
    chapter::ChapterMetadata,
    manga::{Chapter, Manga},
    media::{MediaMetadata, MediaTrait},
};

use managers::{DownloadManager, ImageMessage, MangaManager};

mod setup;

const TEST_NAME: &str = "Myst, Might, Mayhem";

fn test_manga_inst() -> Manga {
    let mut manga = Manga::new(MediaMetadata::new(TEST_NAME.into(), "data/manga".into()));
    manga.insert_chapter(Chapter::new(ChapterMetadata::new(1, "".into())));
    manga
}

fn test_manga_manager() -> MangaManager {
    let mut manager = MangaManager::new(
        "data/manga.json".into(),
        Arc::new(setup::sites_manager()),
        Arc::new(DownloadManager::new()),
    );
    let manga = test_manga_inst();
    manager.repo.insert(manga);
    manager.save().unwrap();
    manager
}

#[test]
fn download_images() {
    ffi::init();
    let manager = test_manga_manager();
    let manga = manager.repo.get_by_name(TEST_NAME).unwrap();
    let rc = manager
        .download_chapter_images(manga, manga.get_chapter(1).unwrap())
        .unwrap();
    for mes in rc {
        match mes {
            ImageMessage::Metadata {
                i,
                width,
                height,
                format,
                size,
            } => {
                dbg!(i, width, height, format, size);
            }
            ImageMessage::Chunk { .. } => (),
            ImageMessage::Error { i, err } => {
                dbg!(i, err);
            }
            ImageMessage::Complete { i, bytes } => {
                let f = File::new(format!("data/images/{TEST_NAME}/{i}.webp"));
                f.save(bytes).unwrap();
            }
        }
    }
}
