#![feature(async_fn_traits)]

mod download;
mod manga;
mod sites;

pub use download::{DownloadManager, ImageMessage};
pub use manga::MangaManager;
pub use sites::SitesManager;
