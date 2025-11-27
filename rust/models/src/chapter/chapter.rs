use serde::{Deserialize, Serialize};

pub trait ChapterTrait {
    const THIS: Vec<String> = Vec::new();

    fn metadata(&self) -> &ChapterMetadata;
}

#[derive(Debug, Default, Serialize, Deserialize)]
pub struct ChapterMetadata {
    pub num: isize,
    pub name: String,
}

impl ChapterMetadata {
    pub fn new(num: isize, name: String) -> Self {
        Self { num, name }
    }
}
