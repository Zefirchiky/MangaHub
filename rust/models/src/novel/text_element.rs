#![allow(refining_impl_trait)]

use std::any::Any;
use std::fmt::Debug;

use models_macros::register_text_element;

use crate::novel::{ParseContext, TokenParsingResult};
use crate::novel::{
    SentenceTrait, Token,
    // sentence::Sentence
};
use crate::registry::ParserRegistry;
use crate::{TEXT_ELEMENT_PARSERS, Parser};

#[derive(Debug, PartialEq, Eq, Clone)]
pub enum ElementEndState {
    /// Curtent TextElement is defenetely finished
    Finished(Option<Token>),
    /// Current TextELement is finished but may be combined wiht next TextElement
    MaybeFinished(Option<Token>),
    /// Current TextElement is defenetely not finished, but first part of Token was wrong, and should be retried
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
    fn try_from_token(token: &Token) -> TokenParsingResult<Self> where Self: Sized;

    /// Will push a token into `TextElement`.
    /// 
    /// If `try_parse_token` is upholding the rules, no empty tokens will be passed.
    fn push_token(&mut self, token: Token) -> ElementEndState;
    
    /// Create a `TextElement` from default Fallback `Narration`
    fn from_narration(narration: Narration, ctx: &ParseContext) -> Self where Self: Sized;

    fn sentences(&self) -> &Vec<Box<dyn SentenceTrait>>;
    fn is_start(&self) -> bool;
    fn is_end(&self) -> bool;
}

pub trait TextElementAuto: Any + TextElement {
    fn type_index(&self) -> usize;
    fn type_name(&self) -> &'static str;
    fn as_any(&self) -> &dyn Any;
    fn as_any_mut(&mut self) -> &mut dyn Any;
}


#[derive(Debug)]
#[allow(dead_code)]
#[register_text_element]
pub struct Dialog {
    /// Represents the character that the dialog is targeting.
    /// TODO: May be not String
    pub to: String,
    /// Represents the character that is talking.
    pub from: String,
    is_opened: bool,
    sentences: Vec<Box<dyn SentenceTrait>>
}

impl TextElement for Dialog {
    // const TYPE_INDEX: usize = Dialog::TYPE_INDEX;
    fn sentences(&self) -> &Vec<Box<dyn SentenceTrait>> {
        &self.sentences
    }

    fn push_token(&mut self, mut token: Token) -> ElementEndState {
        if token.ends_with('\"') {
            if self.is_opened {
                self.is_opened = false;
                let len = token.len();
                token.truncate(len - 1);
                self.sentences.last_mut().unwrap().push(token);
                ElementEndState::Finished(None)
            } else {
                self.is_opened = true;
                let len = token.len();
                let t2 = token.split_off(len - 2);
                ElementEndState::NotFinishedToken(token, t2.into())
            }
        } else if token.starts_with('\"') {
            if !self.is_opened {
                self.is_opened = true;
                token = token[1..].into();
                self.push_token(token)
            } else {
                ElementEndState::Finished(Some(token[1..].to_string().into()))
            }
        } else {
            self.sentences.last_mut().unwrap().push(token);
            ElementEndState::NotFinished
        }
    }

    fn try_from_token(token: &Token) -> TokenParsingResult<Self> {
        if token.starts_with('"') {
            return TokenParsingResult::Matched(Self {
                to: String::new(),
                from: String::new(),
                is_opened: false,
                sentences: vec![ParserRegistry::parse_sentence_token(token)]
            });
        }
        // else if token.ends_with('"') {
            // return TokenParsingResult::MatchedWithBadStart()
        // }
        
        TokenParsingResult::NotMatched
    }
    
    fn from_narration(narration: Narration, _ctx: &ParseContext) -> Self {
        Self {
            from: String::new(),
            to: String::new(),
            is_opened: false,
            sentences: narration.sentences,
        }
    }
    
    fn is_start(&self) -> bool {
        true
    }
    
    fn is_end(&self) -> bool {
        true
    }
}

#[derive(Debug)]
#[allow(dead_code)]
#[register_text_element]
pub struct Thought {
    /// Represents the character that is thinking.
    from: String,
    sentences: Vec<Box<dyn SentenceTrait>>
}

impl TextElement for Thought {
    fn sentences(&self) -> &Vec<Box<dyn SentenceTrait>> {
        &self.sentences
    }
    
    fn push_token(&mut self, token: Token) -> ElementEndState {
        if token.ends_with('\'') {
            ElementEndState::Finished(None)
        } else if token.starts_with('\'') {
            ElementEndState::Finished(Some(token[1..].to_string().into()))
        }else {
            self.sentences.last_mut().unwrap().push(token);
            ElementEndState::NotFinished
        }
    }

    fn try_from_token(token: &Token) -> TokenParsingResult<Self> {
        if token.starts_with('\'') {
            let sentences = if token.is_empty() {
                vec![]
            } else {
                vec![ParserRegistry::parse_sentence_token(token)]
            };
            
            return TokenParsingResult::Matched(Self {
                from: String::new(),
                sentences
            });
        }
        
        TokenParsingResult::NotMatched
    }

    fn from_narration(narration: Narration, _ctx: &ParseContext) -> Self {
        Self {
            from: String::new(),
            sentences: narration.sentences,
        }
    }

    fn is_start(&self) -> bool {
        true
    }

    fn is_end(&self) -> bool {
        true
    }
}


#[derive(Debug)]
pub struct Narration {
    sentences: Vec<Box<dyn SentenceTrait>>
}

impl TextElement for Narration {
    fn sentences(&self) -> &Vec<Box<dyn SentenceTrait>> {
        &self.sentences
    }
    
    fn push_token(&mut self, token: Token) -> ElementEndState {
        
        self.sentences.last_mut().unwrap().push(token);
        ElementEndState::MaybeFinished(None)
    }
    
    fn try_from_token(token: &Token) -> TokenParsingResult<Self> {
        TokenParsingResult::Matched(Self {
            sentences: vec![ParserRegistry::parse_sentence_token(token)]
        })
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