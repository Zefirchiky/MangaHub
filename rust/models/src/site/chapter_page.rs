use log::warn;
use scraper::Html;
use serde::{Deserialize, Serialize};
use url::Url;

use crate::site::Extractor;

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct ChapterPageContent {
    pub name: Option<String>,
    pub image_urls: Option<Vec<Url>>,
    pub text: Option<Vec<String>>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ChapterPage {
    url_template: String,
    name_selector: Option<Extractor>,
    img_selector: Option<Extractor>,
    text_selector: Option<Extractor>,
}

impl ChapterPage {
    pub fn new(
        url_template: String,
        name_selector: Option<Extractor>,
        img_selector: Option<Extractor>,
        text_selector: Option<Extractor>,
    ) -> Self {
        Self {
            url_template,
            name_selector,
            img_selector,
            text_selector,
        }
    }

    pub fn get_url(&self, base: &Url, name_slug: &str, num: isize) -> Url {
        base.join(
            &self
                .url_template
                .replace("{slug}", name_slug)
                .replace("{num}", &num.abs().to_string()), // FIXME: Negative chapters better handling
        )
        .unwrap()
    }

    pub fn parse_html(&self, html: &Html) -> ChapterPageContent {
        let mut content = ChapterPageContent::default();

        if let Some(extractor) = &self.name_selector {
            match extractor.parse_html(html).get(0) {
                Some(name) => content.name = Some(name.clone()), // FIXME: inefficient
                None => warn!("Name was not found with extractor {extractor:#?}"),
            }
        }

        if let Some(extractor) = &self.img_selector {
            let surls: Vec<Url> = extractor
                .parse_html(html)
                .iter()
                .filter_map(|s| Url::parse(s).ok())
                .collect();
            match surls.is_empty() {
                true => warn!("No image urls was not found with extractor {extractor:#?}"),
                false => content.image_urls = Some(surls),
            }
        }

        if let Some(extractor) = &self.text_selector {
            let texts = extractor.parse_html(html);
            match texts.is_empty() {
                true => warn!("No text was not found with extractor {extractor:#?}"),
                false => content.text = Some(texts),
            }
        }

        content
    }
}
