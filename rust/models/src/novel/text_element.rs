#![allow(refining_impl_trait)]

use std::any::Any;
use std::fmt::Debug;

use derive_more::From;
use models_macros::register_text_element;

use crate::novel::{ParseContext, Sentences, TokenParsingResult};
use crate::novel::{
    SentenceTrait,
    Token,
    // sentence::Sentence
};
use crate::registry::ParserRegistry;
use crate::{Parser, TEXT_ELEMENT_PARSERS};

#[derive(Debug, PartialEq, Eq, Clone)]
pub enum ElementEndState {
    /// Curtent TextElement is definitely finished
    Finished(Option<Token>),
    /// Current TextELement is finished but may be combined wiht next TextElement
    MaybeFinished(Option<Token>),
    /// Current TextElement is definitely not finished, but first part of Token was wrong, and should be retried
    ///
    /// # Example
    /// `this"` is a Narration folowed by Dialog, `this` should be tried again, and `"` later.
    ///
    /// `this"` will be parsed as new empty Narration, and after Token is pushed, `this` and `"` should be extracted, making 2 new Tokens to parse.
    ///
    /// `this` will be in an old Narration, while `"` will become a Dialog.
    NotFinishedToken(Token, Token),
    /// Current TextELement is defenetely not finished
    NotFinished,
}

pub trait TextElement: Send + Sync + Debug {
    /// Will try parsing token into `TextElement` based on rules of `Self`.
    fn try_from_token(token: Token) -> TokenParsingResult<Self>
    where
        Self: Sized;

    /// Will push a token into `TextElement`.
    ///
    /// If `try_parse_token` is upholding the rules, no empty tokens will be passed.
    fn push_token(&mut self, token: Token) -> ElementEndState;

    /// Create a `TextElement` from default Fallback `Narration`
    fn from_narration(narration: Narration, ctx: &ParseContext) -> Self
    where
        Self: Sized;

    fn start_chars() -> &'static str
    where
        Self: Sized,
    {
        ""
    }
    fn end_chars() -> &'static str
    where
        Self: Sized,
    {
        ""
    }

    fn sentences(&self) -> &Sentences;
    fn is_start(&self) -> bool;
    fn is_end(&self) -> bool;
}

pub trait TextElementAuto: Any + TextElement {
    fn type_index(&self) -> usize;
    fn type_name(&self) -> &'static str;
    fn as_any(&self) -> &dyn Any;
    fn as_any_mut(&mut self) -> &mut dyn Any;
}

#[derive(Debug, Default, From)]
#[allow(dead_code)]
#[register_text_element]
pub struct Dialog {
    /// Represents the character that the dialog is targeting.
    /// TODO: May be not String
    pub to: String,
    /// Represents the character that is talking.
    pub from: String,
    is_opened: bool,
    sentences: Sentences,
}

impl TextElement for Dialog {
    // const TYPE_INDEX: usize = Dialog::TYPE_INDEX;
    fn sentences(&self) -> &Sentences {
        &self.sentences
    }

    fn push_token(&mut self, mut token: Token) -> ElementEndState {
        if let Some(at) = token.find('"') {
            if self.is_opened {
                self.is_opened = false;
                let mut to_push = token.split_off(at);
                to_push = to_push.split_off(1);
                if !token.is_empty() {
                    self.sentences.push(token.into());
                }
                ElementEndState::Finished(Token::new(to_push).into())
            } else {
                token = token.split_off(1).into();
                if token.is_empty() {
                    self.is_opened = true;
                    ElementEndState::NotFinished
                } else {
                    if let Some(at2) = token.find('"') {      // '"' can only be at the start if Dialog is not opened
                        token.truncate(at);                 // Remove '"'+ from token
                        let to_push = token.split_off(at2);
                        if !to_push.is_empty() {
                            self.sentences.push(to_push.into());
                        }
                        ElementEndState::Finished(token.into())
                    } else {
                        self.is_opened = true;
                        token.truncate(at);
                        if !token.is_empty() {
                            self.sentences.push(token.into());
                        }
                        ElementEndState::NotFinished
                    }
                }
            }
        } else {
            self.sentences.push(token);
            ElementEndState::NotFinished
        }
    }

    fn try_from_token(mut token: Token) -> TokenParsingResult<Self> {
        // dbg!(&token);
        if let Some(at) = token.find('"') {
            let back_token = if at == 0 {
                None
            } else {
                Some(token.split_off(at).into())
            };
            let mut forward_token = None;
            let matched = if let Some(at_end) = token.find('"') {
                let m = token.split_off(at_end).into();
                if !token.is_empty() {
                    forward_token = Some(token);
                }
                m
            } else {
                token
            };
            return TokenParsingResult::Matched {
                model: Self {
                    to: String::new(),
                    from: String::new(),
                    is_opened: false,
                    sentences: vec![].into(),
                },
                matched,
                prev: back_token,
                next: forward_token,
            };
        }

        TokenParsingResult::NotMatched(token)
    }

    fn from_narration(narration: Narration, _ctx: &ParseContext) -> Self {
        Self {
            from: String::new(),
            to: String::new(),
            is_opened: false,
            sentences: narration.sentences,
        }
    }

    fn start_chars() -> &'static str
    where
        Self: Sized,
    {
        "\""
    }

    fn end_chars() -> &'static str
    where
        Self: Sized,
    {
        "\""
    }

    fn is_start(&self) -> bool {
        true
    }

    fn is_end(&self) -> bool {
        true
    }
}

#[derive(Debug, Default, From)]
#[allow(dead_code)]
#[register_text_element]
pub struct Thought {
    /// Represents the character that is thinking.
    from: String,
    is_opened: bool,
    sentences: Sentences,
}

impl TextElement for Thought {
    fn sentences(&self) -> &Sentences {
        &self.sentences
    }

    fn push_token(&mut self, mut token: Token) -> ElementEndState {
        if let Some(at) = token.find('\'') {
            if self.is_opened {
                self.is_opened = false;
                let mut to_push = token.split_off(at);
                to_push = to_push.split_off(1);
                if !token.is_empty() {
                    self.sentences.push(token.into());
                }
                ElementEndState::Finished(Token::new(to_push).into())
            } else {
                token = token.split_off(1).into();
                if token.is_empty() {
                    self.is_opened = true;
                    ElementEndState::NotFinished
                } else {
                    if let Some(at2) = token.find('\'') {      // '"' can only be at the start if Dialog is not opened
                        token.truncate(at);                 // Remove '"'+ from token
                        let to_push = token.split_off(at2);
                        if !to_push.is_empty() {
                            self.sentences.push(to_push.into());
                        }
                        ElementEndState::Finished(token.into())
                    } else {
                        self.is_opened = true;
                        token.truncate(at);
                        if !token.is_empty() {
                            self.sentences.push(token.into());
                        }
                        ElementEndState::NotFinished
                    }
                }
            }
        } else {
            self.sentences.push(token);
            ElementEndState::NotFinished
        }
    }

    fn try_from_token(mut token: Token) -> TokenParsingResult<Self> {
        if let Some(at) = token.find('\'') {
            let back_token = if at == 0 {
                None
            } else {
                Some(token.split_off(at).into())
            };
            let mut forward_token = None;
            let matched = if let Some(at_end) = token.find('"') {
                let m = token.split_off(at_end).into();
                if !token.is_empty() {
                    forward_token = Some(token);
                }
                m
            } else {
                token
            };
            return TokenParsingResult::Matched {
                model: Self {
                    from: String::new(),
                    is_opened: false,
                    sentences: vec![].into(),
                },
                matched,
                prev: back_token,
                next: forward_token,
            };
        }

        TokenParsingResult::NotMatched(token)
    }

    fn from_narration(narration: Narration, _ctx: &ParseContext) -> Self {
        Self {
            from: String::new(),
            is_opened: false,
            sentences: narration.sentences,
        }
    }

    fn start_chars() -> &'static str
    where
        Self: Sized,
    {
        "'"
    }

    fn end_chars() -> &'static str
    where
        Self: Sized,
    {
        "'"
    }

    fn is_start(&self) -> bool {
        true
    }

    fn is_end(&self) -> bool {
        true
    }
}

#[derive(Debug, Default, From)]
#[from(forward)]
pub struct Narration {
    sentences: Sentences,
}

impl Narration {
    pub fn new(token: Token) -> (Self, Token) {
        (
            Self {
                sentences: vec![ParserRegistry::parse_sentence_token(&token)].into(),
            },
            token,
        )
    }
}

impl TextElement for Narration {
    fn sentences(&self) -> &Sentences {
        &self.sentences
    }

    fn push_token(&mut self, token: Token) -> ElementEndState {
        self.sentences.last_mut().unwrap().push(token);
        ElementEndState::MaybeFinished(None)
    }

    fn try_from_token(token: Token) -> TokenParsingResult<Self> {
        let (el, tok) = Self::new(token);
        TokenParsingResult::Matched {
            model: el,
            matched: tok,
            prev: None,
            next: None,
        }
    }

    fn from_narration(narration: Narration, _ctx: &ParseContext) -> Self {
        narration
    }

    fn is_start(&self) -> bool {
        true
    }

    fn is_end(&self) -> bool {
        true
    }
}

impl TextElementAuto for Narration {
    fn type_index(&self) -> usize {
        0
    }

    fn type_name(&self) -> &'static str {
        "Narration"
    }

    fn as_any(&self) -> &dyn Any {
        self
    }

    fn as_any_mut(&mut self) -> &mut dyn Any {
        self
    }
}
