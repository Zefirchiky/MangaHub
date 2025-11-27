use scraper::{Html, Selector};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub enum DataSource {
    Text(u32),
    Attr(String),
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Extractor {
    pub selector: Selector,
    pub source: DataSource,
}

impl Extractor {
    pub fn new(selector: &str, source: DataSource) -> Self {
        Self {
            selector: Selector::parse(selector).expect(&format!("Selector `{selector}` is wrong")),
            source,
        }
    }

    pub fn parse_html(&self, html: &Html) -> Vec<String> {
        let mut el = vec![];
        for e in html.select(&self.selector) {
            el.push(match &self.source {
                DataSource::Attr(attr) => match e.attr(attr) {
                    Some(s) => s.to_owned(),
                    None => continue,
                },
                DataSource::Text(_) => match e.text().next() {
                    Some(s) => s.to_owned(),
                    None => continue,
                },
            });
        }
        el
    }
}
