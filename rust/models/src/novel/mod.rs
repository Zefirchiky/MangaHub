mod novel;
mod chapter;
mod paragraph;
pub mod text_element;
mod sentence;
mod word;
mod token;
mod context;
mod repo;

pub use novel::Novel;
pub use chapter::{Chapter};
pub use paragraph::Paragraph;
pub use text_element::{TextElement, ElementEndState};
pub use sentence::{SentenceTrait, Sentence};
pub use word::WordTrait;
pub use token::{Token, TokenParsingResult, ParseContext};
pub use context::{Context, NovelContext, ChapterContext, ParagraphContext};
pub use repo::ChaptersRepo;