use serde::{Deserialize, Serialize};

use crate::novel::{Paragraph, Token};
use crate::chapter::{ChapterMetadata, ChapterTrait};

#[allow(dead_code)]
#[derive(Debug, Serialize, Deserialize)]
pub struct Chapter {
    metadata: ChapterMetadata,
    #[serde(skip)]
    paragraphs: Vec<Paragraph>
}

impl Chapter {
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

impl ChapterTrait for Chapter {
    fn metadata(&self) -> &ChapterMetadata {
        &self.metadata
    }
}