use serde::{Deserialize, Serialize};

pub trait ChapterTrait {
    const THIS: Vec<String> = Vec::new();

    fn metadata(&self) -> &ChapterMetadata;
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ChapterMetadata {
    pub num: i32,
    pub name: String
}

// impl ChapterMetadata {
//     fn new(num: i32, name: String) -> Self {
//         Self {
//             num,
//             name,
//         }
//     }
// }