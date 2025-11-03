use std::{fs::File, io::{BufReader, Read, Seek}, path::Path};

use image::{ImageReader};

#[derive(Debug, thiserror::Error)]
pub enum FromFileError {
    #[error("I/O Error: {0}")]
    Io(#[from] std::io::Error),
    #[error("Image Error: {0}")]
    Image(#[from] image::ImageError),
}

pub struct Image<R: Read + Seek> {
    pub img: ImageReader<R>,
}

impl<R: Read + Seek> Image<R> {
    pub fn new(img: ImageReader<R>) -> Self {
        Self {
            img
        }
    }

    pub fn from_file(file: impl AsRef<Path>) -> Result<Image<BufReader<File>>, FromFileError> {
        Ok(Image {
            img: image::ImageReader::open(file)?
        })
    }
}

impl<R: Read + Seek> From<ImageReader<R>> for Image<R> {
    fn from(value: ImageReader<R>) -> Self {
        Self::new(value)
    }
}

impl<R: Read + Seek> std::ops::Deref for Image<R> {
    type Target = ImageReader<R>;
    fn deref(&self) -> &Self::Target {
        &self.img
    }
}

impl<R: Read + Seek> std::ops::DerefMut for Image<R> {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.img
    }
}