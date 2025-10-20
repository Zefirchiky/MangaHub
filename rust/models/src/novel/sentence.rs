use std::{any::Any, fmt::Debug};

use crate::novel::{Token};

pub trait SentenceTrait: Any + Sync + Send + Debug {
    fn from_token(token: &Token) -> Box<Self> where Self: Sized;
    fn push(&mut self, token: Token);
}

#[derive(Debug)]
pub struct Sentence {
    // words: Vec<Box<dyn WordTrait>>
    words: Vec<Token>
}

impl SentenceTrait for Sentence {
    fn from_token(_: &Token) -> Box<Self> {
        Box::new(Self { words: vec![] })
    }

    fn push(&mut self, token: Token) {
        self.words.push(token);
    }
}