use crate::novel::{Paragraph, Token};

#[allow(dead_code)]
pub struct NovelChapter {
    metadata: ChapterMetadata,
    paragraphs: Vec<Paragraph>
}

impl NovelChapter {
    pub fn new(metadata: ChapterMetadata) -> Self {
        Self {
            metadata,
            paragraphs: vec![Paragraph::new()]
        }
    }

    pub fn push_token(mut self, token: String) -> Self {
        if token.is_empty() {
            return self;
        }
        self.paragraphs.last_mut().unwrap().push_token(Token::new(token));
        self
    }
}

impl ChapterTrait for NovelChapter {
    fn metadata(&self) -> &ChapterMetadata {
        &self.metadata
    }
}

pub trait ChapterTrait {
    const THIS: Vec<String> = Vec::new();

    fn metadata(&self) -> &ChapterMetadata;
}

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