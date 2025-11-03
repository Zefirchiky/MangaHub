use std::io::Cursor;

use image::{DynamicImage, ImageReader, Rgb32FImage};

use crate::image::Image;

/// `Image` stored in `ram`
pub struct RamImage {
    img: Image<Cursor<bytes::Bytes>>
}

impl RamImage {
    pub fn new(b: bytes::Bytes) -> Self {
        Self::from_cursor(Cursor::new(b))
    }

    pub fn from_cursor(cursor: Cursor<bytes::Bytes>) -> Self {
        Self::from_image_reader(ImageReader::new(cursor))
    }

    pub fn from_image_reader(reader: ImageReader<Cursor<bytes::Bytes>>) -> Self {
        Self {
            img: reader.into()
        }
    }

    pub fn into_bytes(self) -> bytes::Bytes {
        self.img.img.into_inner().into_inner()
    }

    pub fn compress_jxl(self) -> Vec<u8> {
        let pixmap = self.img.img.decode().expect("Failed to decode image").into_rgb8();
        let mut encoder = jpegxl_rs::encode::encoder_builder()
            .decoding_speed(0)
            .lossless(true)
            .build()
            .expect("Failed to build JxlEncoder");
        let res = encoder.encode(pixmap.as_raw(), pixmap.width(), pixmap.height()).unwrap();
        res.data
    }
}

impl From<ImageReader<Cursor<bytes::Bytes>>> for RamImage {
    fn from(value: ImageReader<Cursor<bytes::Bytes>>) -> Self {
        Self::from_image_reader(value)
    }
}

impl std::ops::Deref for RamImage {
    type Target = Image<Cursor<bytes::Bytes>>;
    fn deref(&self) -> &Self::Target {
        &self.img
    }
}

impl std::ops::DerefMut for RamImage {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.img
    }
}