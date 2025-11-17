use log::warn;
use scraper::Html;
use serde::{Deserialize, Serialize};
use url::Url;

use crate::site::Extractor;

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct MediaPageContent {
    pub name: Option<String>,
    pub cover_url: Option<Url>,
    pub last_chapter_num: Option<isize>
}

#[derive(Debug, Serialize, Deserialize)]
pub struct MediaPage {
    url_template: String,
    name_selector: Option<Extractor>,
    cover_selector: Option<Extractor>,
    last_chapter_num_selector: Option<Extractor>,
}

impl MediaPage {
    pub fn new(
        url_template: String,
        name_selector: Option<Extractor>,
        cover_selector: Option<Extractor>,
        last_chapter_num_selector: Option<Extractor>,
    ) -> Self {
        Self {
            url_template,
            name_selector,
            cover_selector,
            last_chapter_num_selector,
        }
    }

    pub fn get_url(&self, base: &Url, name_slug: &str) -> Url {
        base.join(&self.url_template.replace("{slug}", name_slug))
            .unwrap()
    }

    pub fn parse_html(&self, html: &Html) -> MediaPageContent {
        let mut content = MediaPageContent::default();

        if let Some(extractor) = &self.name_selector {
            match extractor.parse_html(html).get(0) {
                Some(name) => content.name = Some(name.clone()), // FIXME: May be inefficient
                None => warn!("Name was not found with extractor {extractor:#?}"),
            }
        }

        if let Some(extractor) = &self.cover_selector {
            match extractor.parse_html(html).get(0) {
                Some(surl) => {
                    match Url::parse(surl) {
                        Ok(purl) => content.cover_url = Some(purl),
                        Err(err) => warn!("Failed to parse {surl}: {err:#?}"),
                    }
                }
                None => warn!("Cover url was not found with extractor {extractor:#?}")
            }
        }

        if let Some(extractor) = &self.last_chapter_num_selector {
            match extractor.parse_html(html).get(0) {
                Some(num_str) => {
                    let digits: String = num_str
                        .chars()
                        .filter(|c| c.is_numeric())
                        .collect();
                    match digits.is_empty() {
                        true => warn!("Failed to extract a last chapter number from string `{num_str}`"),
                        false => content.last_chapter_num = digits.parse::<isize>().ok(),
                    }
                }
                None => warn!("Last chapter number was not found with extractor {extractor:#?}")
            }
        }

        content
    }
}
