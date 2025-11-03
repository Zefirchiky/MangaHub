use image::DynamicImage;

#[derive(Debug, Default)]
pub struct Pixmap {
    pub img: DynamicImage,
}

impl Pixmap {
    pub fn new(img: DynamicImage) -> Self {
        Self {
            img
        }
    }
}

impl From<DynamicImage> for Pixmap {
    fn from(value: DynamicImage) -> Self {
        Self::new(value)
    }
}

impl std::ops::Deref for Pixmap {
    type Target = DynamicImage;
    fn deref(&self) -> &Self::Target {
        &self.img
    }
}

impl std::ops::DerefMut for Pixmap {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.img
    }
}