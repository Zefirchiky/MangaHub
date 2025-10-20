use std::sync::OnceLock;

use crate::{novel::{text_element::{Narration, TextElementAuto}, Sentence, SentenceTrait, TextElement, Token, TokenParsingResult}, Parser};
static GLOBAL_REGISTRY: OnceLock<ParserRegistry> = OnceLock::new();

pub fn init_registry() {
    GLOBAL_REGISTRY.get_or_init(|| ParserRegistry::new());
}

pub struct ParserRegistry {
    _text_element_parsers: &'static [Parser]
}

impl ParserRegistry {
    pub fn new() -> Self {
        Self {
            _text_element_parsers: &crate::TEXT_ELEMENT_PARSERS
        }
    }

    pub fn parse_text_element_token(token: &Token) -> Box<dyn TextElementAuto> {
        for f in crate::TEXT_ELEMENT_PARSERS {
            if let TokenParsingResult::Matched(el) = (f.from_token)(token) {
                return el;
            }
        }

        Box::new(Narration::try_from_token(token).unwrap())
    }

    pub fn parse_sentence_token(token: &Token) -> Box<dyn SentenceTrait> {
        Sentence::from_token(&token)
    }
}