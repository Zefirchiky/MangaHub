use managers::SitesManager;
use models::site::{ChapterPage, DataSource, Extractor, MediaPage, Site};
use url::Url;

pub fn site() -> Site {
    let site = Site::new(
        "AsuraScans".to_string(),
        Url::parse("https://asurascanz.com").unwrap(),
        MediaPage::new(
            "manga/{slug}".to_string(),
            Some(Extractor::new(
                "div#titlemove h1.entry-title",
                DataSource::Text(0),
            )),
            Some(Extractor::new(
                "div.thumb img",
                DataSource::Attr("src".to_string()),
            )),
            Some(Extractor::new("span.chapternum", DataSource::Text(0))),
        ),
        ChapterPage::new(
            "{slug}-chapter-{num}".to_string(),
            None,
            Some(Extractor::new(
                "div#readerarea p img.lazyload",
                DataSource::Attr("data-src".to_string()),
            )),
            None,
        ),
    );
    // let id = sites_manager.add(site);
    // let site = sites_manager.repo.get_by_name("AsuraScans").unwrap();

    // let html = sites_manager
    //     .download_chapter_content_blocking(
    //         [site.id].to_vec(),
    //         "myst-might-mayhem".to_string(),
    //         94,
    //     )
    //     .unwrap();
    // if let Some(urls) = html.image_urls {
    //     let rc = DownloadManager::new().download_images_blocking(urls);
    //     for message in rc {
    //         if let ImageMessage::Complete { i, bytes } = message {
    //             let image_f = handlers::file::File::new(format!("test_full/{i}.webp"));
    //             image_f.save(bytes).unwrap();
    //         }
    //     }
    // }

    site
}

pub fn sites_manager() -> SitesManager {
    let mut sites_manager = SitesManager::new("data/sites/test_sites.json".into());
    sites_manager.load();

    if sites_manager.repo.get_by_name("AsuraScans").is_none() {
        sites_manager.add(site());
        sites_manager.save();
    }

    for (id, site) in sites_manager.repo.iter() {
        log::warn!("{id} {}", site.name)
    }

    sites_manager
}
