use std::{
    fs::File,
    io::{BufReader, Read, Seek},
    path::Path,
};

use derive_more::{Debug, Deref, DerefMut, From};
use image::ImageReader;

#[derive(Debug, thiserror::Error)]
pub enum FromFileError {
    #[error("I/O Error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Image Error: {0}")]
    Image(#[from] image::ImageError),
}

#[derive(Debug, From, Deref, DerefMut)]
pub struct Image<R: Read + Seek> {
    pub img: ImageReader<R>,
}

impl<R: Read + Seek> Image<R> {
    pub fn new(img: ImageReader<R>) -> Self {
        Self { img }
    }

    pub fn from_file(file: impl AsRef<Path>) -> Result<Image<BufReader<File>>, FromFileError> {
        Ok(Image {
            img: image::ImageReader::open(file)?,
        })
    }
}