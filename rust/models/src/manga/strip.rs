use serde::{Deserialize, Serialize};

use crate::image::Pixmap;

#[derive(Debug, Serialize, Deserialize)]
pub enum StripType {
    Uniform,
    ContentAware,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Strip {
    index: usize,
    start_y: usize,
    finish_y: usize,
    #[serde(skip)]
    pub pixmap: Pixmap,
}
