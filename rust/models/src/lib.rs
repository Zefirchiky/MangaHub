#![feature(
    type_alias_impl_trait,
    default_field_values,
)]
#![allow(refining_impl_trait)]
pub mod media;
pub mod novel;
pub mod manga;
pub mod chapter;
pub mod repos;
pub mod cache;
pub mod character;
pub mod image;
pub mod registry;

use linkme::distributed_slice;

use crate::novel::{text_element::{Narration, TextElementAuto}, ParseContext, TokenParsingResult, Token};

pub fn init() {
    assert!(jxl_oxide::integration::register_image_decoding_hook(), "Init function should only be called once! jxl_oxide error");
}

/// Parser with explicit ordering hint
struct Parser {
    pub name: &'static str,
    /// Ordering hint: Fallback = last, Normal = middle, Priority = first
    // pub order: ParserOrder,
    pub from_token: fn(Token) -> TokenParsingResult<Box<dyn TextElementAuto>>,
    pub from_narration: fn(Narration, &ParseContext) -> Box<dyn TextElementAuto>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
enum ParserOrder {
    Highest = 0,
    High = 1,
    MediumHgh = 2,
    Medium = 3,
    MediumLow = 4,
    Low = 5,
}

/// The distributed slice that collects all parsers at link time
#[distributed_slice]
pub static TEXT_ELEMENT_PARSERS: [Parser] = [..];