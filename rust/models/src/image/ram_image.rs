use std::io::Cursor;

use derive_more::{Debug, Deref, DerefMut, From};
use image::ImageReader;

use crate::image::Image;

/// `Image` stored in `ram`
#[derive(Debug, From, Deref, DerefMut)]
#[from(forward)]
pub struct RamImage {
    #[debug(skip)]
    img: Image<Cursor<bytes::Bytes>>,
}

impl RamImage {
    pub fn new(b: bytes::Bytes) -> Self {
        Self::from_cursor(Cursor::new(b))
    }

    pub fn from_cursor(cursor: Cursor<bytes::Bytes>) -> Self {
        Self::from_image_reader(ImageReader::new(cursor))
    }

    pub fn from_image_reader(reader: ImageReader<Cursor<bytes::Bytes>>) -> Self {
        Self { img: reader.into() }
    }

    pub fn into_bytes(self) -> bytes::Bytes {
        self.img.img.into_inner().into_inner()
    }

    // pub fn compress_jxl(self) -> Vec<u8> {
    //     let pixmap = self.img.img.decode().expect("Failed to decode image").into_rgb8();
    //     let mut encoder = jpegxl_rs::encode::encoder_builder()
    //         .decoding_speed(0)
    //         .lossless(true)
    //         .build()
    //         .expect("Failed to build JxlEncoder");
    //     let res = encoder.encode(pixmap.as_raw(), pixmap.width(), pixmap.height()).unwrap();
    //     res.data
    // }
}
