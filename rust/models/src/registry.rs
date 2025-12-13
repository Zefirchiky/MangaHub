use std::sync::OnceLock;

use crate::{
    Parser,
    novel::{
        Sentence, SentenceTrait, Token, TokenParsingResult,
        text_element::{Narration, TextElementAuto},
    },
};

pub static GLOBAL_REGISTRY: OnceLock<ParserRegistry> = OnceLock::new();

pub fn init_registry() {
    GLOBAL_REGISTRY.get_or_init(|| ParserRegistry::new());
}

pub struct ParserRegistry {
    _text_element_parsers: &'static [Parser],
}

impl ParserRegistry {
    pub fn new() -> Self {
        Self {
            _text_element_parsers: &crate::TEXT_ELEMENT_PARSERS,
        }
    }

    pub fn parse_text_element_token(
        mut token: Token,
    ) -> (Box<dyn TextElementAuto>, Token, Option<Token>, Option<Token>) {
        // `This"` -> `This` & `"`      Matched `"` with `This` as rest
        // `This"` -> `This` & Dialog   Matched Dialog with `This` as rest
        // `This"` -> `This` -> `"`     Matched `Narration(This)` with `"` as rest
        // Function sees `"`, returns everything before, and `"` -> Parse them in a queue again
        // let mut result: TokenParsingResult<Box<dyn TextElementAuto>> = TokenParsingResult::MatchedWithRest(token, Token::new(""));
        // let mut return_tokens: Vec<Token> = Vec::with_capacity(10);
        // while let TokenParsingResult::MatchedWithRest(t1, t2) = &mut result {
        for f in crate::TEXT_ELEMENT_PARSERS {
            match (f.from_token)(token) {
                TokenParsingResult::Matched {
                    model,
                    matched,
                    prev: not_matched_back,
                    next: not_matched_forward,
                } => return (model, matched, not_matched_back, not_matched_forward),
                // Pass first token as element, and second as the rest
                TokenParsingResult::NotMatched(t) => token = t,
            }
        }

        // }
        let (el, token) = Narration::new(token);
        (Box::new(el), token, None, None)
    }

    pub fn parse_sentence_token(token: &Token) -> Box<dyn SentenceTrait> {
        Sentence::from_token(&token)
    }
}
