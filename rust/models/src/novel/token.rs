use std::{ops::{Deref, DerefMut}};

/// A part of text, divided by ' ' (space)
#[derive(Debug, PartialEq, Eq, Clone)]
pub struct Token(String);

impl Token {
    pub fn new(s: impl Into<String>) -> Self {
        Self(s.into())
    }

    pub fn as_str(&self) -> &str {
        &self.0
    }
}

impl Deref for Token {
    type Target = String;
    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl DerefMut for Token {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.0
    }
}

impl From<String> for Token {
    fn from(s: String) -> Self {
        Self(s)
    }
}

impl From<&str> for Token {
    fn from(s: &str) -> Self {
        Self(s.into())
    }
}

pub struct ParseContext {}

pub enum TokenParsingResult<T> {
    Matched(T, Token),
    MatchedWithRest(Token, Token),
    NotMatched(Token),
}

// impl<T> TokenParsingResult<T> {
//     pub fn unwrap(self) -> T {
//         match self {
//             Self::Matched(el) => el,
//             Self::NotMatched => panic!("What the fuck"),
//         }
//     }
// }