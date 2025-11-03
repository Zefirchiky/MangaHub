use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct Size {
    height: usize,
    width: usize,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Image {
    size: Size,
    index: usize,
}