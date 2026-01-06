use std::{any::Any, fmt::Debug};

use derive_more::{Deref, DerefMut, From};

use crate::{novel::{Context, Token}, registry::ParserRegistry};

pub trait WordTrait: Any + Sync + Sync + Debug {
    fn try_from_token(token: Token, ctx: Context) -> Self where Self: Sized;
    fn is_complete(&self) -> bool;
}

#[derive(Debug)]
pub enum WordCandidate {
    Candidates(Vec<Word>),
    Word(Word),
}

#[derive(Debug)]
pub enum Word {
    Normal(NormalWord),
    Punctuation(Punctuation),
    Name(Name),
}

#[derive(Debug, Default, Deref, DerefMut, From)]
pub struct WordsVec(Vec<WordCandidate>);

impl WordsVec {
    pub fn push_token(&mut self, token: Token) {
        match self.last_mut() {
            Some(word) => {
                if word.is_complete() {
                    self.0.push(ParserRegistry::parse_word_token(token))
                } else {
                    word.push_token(token)
                }
            },
            None => {
                let mut sent = ParserRegistry::parse_word_token(&token);
                sent.push(token);
                self.0.push(sent);
            }
        }
    }
}

#[derive(Debug, Default, From, Deref, DerefMut)]
#[from(forward)]
#[allow(dead_code)]
pub struct NormalWord {
    #[deref]
    #[deref_mut]
    pub word: String,
    pub suggestions: Vec<String>,
}

#[derive(Debug)]
pub struct Punctuation {
    pub word: String,
}

impl WordTrait for Punctuation {
    fn is_complete(&self) -> bool {
        true
    }

    fn try_from_token(token: Token, _ctx: Context) -> Self where Self: Sized {
        Self {
            word: token.to_string(),
        }
    }
}

#[derive(Debug)]
#[allow(dead_code)]
pub struct Name {
    pub character: String,
    pub has_name: bool,
    pub has_surname: bool,
    pub candidate_names: Vec<String>,
    pub candidate_surnames: Vec<String>,
}
