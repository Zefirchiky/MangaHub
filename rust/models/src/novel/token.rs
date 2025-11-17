use derive_more::{Deref, DerefMut, From};

/// A part of text, divided by ' ' (space)
#[derive(Debug, Default, PartialEq, Eq, Clone, From, Deref, DerefMut)]
#[from(forward)]
pub struct Token(String);

impl Token {
    pub fn new(s: impl Into<String>) -> Self {
        Self(s.into())
    }

    pub fn as_str(&self) -> &str {
        &self.0
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
