use derive_more::{From};
use serde::{Deserialize, Serialize};

use crate::manga::{Strip, StripType};

#[derive(Debug, From, Serialize, Deserialize)]
pub struct Size {
    pub height: usize,
    pub width: usize,
}

#[derive(Debug, From, Serialize, Deserialize)]
pub struct Panel {
    pub size: Size,
    pub index: usize,
    pub strips_type: StripType,
    pub strips: Vec<Strip>,
    pub image_name: String,
}
