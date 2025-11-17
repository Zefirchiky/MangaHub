use derive_more::{Deref, DerefMut, From};
use image::DynamicImage;

#[derive(Debug, Default, From, Deref, DerefMut)]
#[from(forward)]
pub struct Pixmap {
    pub img: DynamicImage,
}

impl Pixmap {
    pub fn new(img: DynamicImage) -> Self {
        Self { img }
    }
}