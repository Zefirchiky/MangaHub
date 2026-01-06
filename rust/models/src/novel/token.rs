use derive_more::{Deref, DerefMut, From};

/// A part of text, divided by ' ' (space)
#[derive(Debug, Default, PartialEq, Eq, Clone, From, Deref, DerefMut)]
#[from(forward)]
pub struct Token(String);

impl Token {
    /// Creates a new Token from a string.
    ///
    /// Panics if the string is empty or contains a space.
    pub fn new(s: impl Into<String>) -> Self {
        let s = s.into();
        assert!(!s.is_empty(), "Token should not be empty");
        assert!(!s.contains(' '), "Token should not contain spaces, given `{s}`");
        Self(s)
    }

    pub fn try_new(s: impl Into<String>) -> Option<Self> {
        let s = s.into();
        if s.is_empty() || s.contains(' ') {
            None
        } else {
            Some(Self(s))
        }
    }
}

pub struct ParseContext {}

pub enum TokenParsingResult<T> {
    Matched {
        model: T,
        matched: Token,
        prev: Option<Token>,
        next: Option<Token>,
    },
    // MatchedWithRest(Token, Token),
    NotMatched(Token),
}
