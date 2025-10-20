mod base;
mod chapter;
mod paragraph;
pub mod text_element;
mod sentence;
mod word;
mod token;
mod repo;

pub use base::Novel;
pub use chapter::{NovelChapter, ChapterTrait, ChapterMetadata};
pub use paragraph::Paragraph;
pub use text_element::{TextElement, ElementEndState};
pub use sentence::{SentenceTrait, Sentence};
pub use word::WordTrait;
pub use token::{Token, TokenParsingResult, ParseContext};
pub use repo::ChaptersRepo;