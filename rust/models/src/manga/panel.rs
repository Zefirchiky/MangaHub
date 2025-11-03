use serde::{Deserialize, Serialize};

use crate::manga::{Strip, StripType};

#[derive(Debug, Serialize, Deserialize)]
pub struct Size {
    height: usize,
    width: usize,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Panel {
    size: Size,
    index: usize,
    strips_type: StripType,
    strips: Vec<Strip>,
    image_name: String,
}