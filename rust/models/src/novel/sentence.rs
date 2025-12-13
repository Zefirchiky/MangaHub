use std::{any::Any, fmt::Debug};

use derive_more::{Deref, DerefMut, From};

use crate::{novel::Token, registry::ParserRegistry};

pub trait SentenceTrait: Any + Sync + Send + Debug {
    fn from_token(token: &Token) -> Box<Self>
    where
        Self: Sized;
    fn push(&mut self, token: Token);
}

#[derive(Debug, Default, Deref, DerefMut, From)]
pub struct Sentences(Vec<Box<dyn SentenceTrait>>);

impl Sentences {
    pub fn push(&mut self, token: Token) {
        match self.last_mut() {
            Some(sent) => sent.push(token),
            None => {
                let mut sent = ParserRegistry::parse_sentence_token(&token);
                sent.push(token);
                self.0.push(sent);
            }
        }
    }
}

#[derive(Debug)]
pub struct Sentence {
    // words: Vec<Box<dyn WordTrait>>
    words: Vec<Token>,
}

impl SentenceTrait for Sentence {
    fn from_token(_: &Token) -> Box<Self> {
        Box::new(Self { words: vec![] })
    }

    fn push(&mut self, token: Token) {
        self.words.push(token);
    }
}
