use std::marker::PhantomData;

use image::DynamicImage;

use crate::image::Pixmap;

pub struct LowQuality;
pub struct HighQuality;

pub trait QualityState {}
impl QualityState for LowQuality {}
impl QualityState for HighQuality {}

pub struct StripPixmap<Q: QualityState> {
    pixmap: Pixmap,
    _qual: PhantomData<Q>,
}

impl<Q: QualityState> StripPixmap<Q> {
    pub fn new(pixmap: Pixmap) -> Self {
        Self {
            pixmap,
            _qual: PhantomData::<Q>,
        }
    }

    pub fn resize(&self, factor: f32) -> StripPixmap<HighQuality> {
        self.img.resize(
            (self.width() as f32 * factor) as u32,
            (self.height() as f32 * factor) as u32,
            image::imageops::FilterType::Nearest
        ).into()
    }
}

impl StripPixmap<LowQuality> {
    pub fn upgrade(pixmap: Pixmap) -> StripPixmap<HighQuality> {
        StripPixmap::new(pixmap)
    }
}

impl StripPixmap<HighQuality> {
    pub fn downgrade(pixmap: Pixmap) -> StripPixmap<LowQuality> {
        StripPixmap::new(pixmap)
    }
}

impl<Q: QualityState> From<Pixmap> for StripPixmap<Q> {
    fn from(value: Pixmap) -> Self {
        StripPixmap::new(value)
    }
}

impl<Q: QualityState> From<DynamicImage> for StripPixmap<Q> {
    fn from(value: DynamicImage) -> Self {
        StripPixmap::new(Pixmap::new(value))
    }
}

impl<Q: QualityState> std::ops::Deref for StripPixmap<Q> {
    type Target = Pixmap;
    fn deref(&self) -> &Self::Target {
        &self.pixmap
    }
}

impl<Q: QualityState> std::ops::DerefMut for StripPixmap<Q> {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.pixmap
    }
}