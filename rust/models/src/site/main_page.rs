use serde::{Deserialize, Serialize};
use url::Url;

#[derive(Debug, Serialize, Deserialize)]
pub struct MainPage {
    url_template: String,
}

impl MainPage {
    pub fn new(url_template: String) -> Self {
        Self {
            url_template
        }
    }

    pub fn get_url(&self, base: Url, name_slug: String, num: isize) -> Url {
        base.join(&self.url_template
            .replace("{slug}", &name_slug)
            .replace("{num}", &num.abs().to_string())   // FIXME: Negative chapters better handling
        ).unwrap()
    }
}