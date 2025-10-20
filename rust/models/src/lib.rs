#![feature(type_alias_impl_trait, default_field_values)]
pub mod novel;
pub mod registry;

use linkme::distributed_slice;

use crate::novel::{text_element::{Narration, TextElementAuto}, ParseContext, TokenParsingResult, Token};


// pub struct Parser {
    //     pub name: &'static str,
    //     /// Ordering hint: Fallback = last, Normal = middle, Priority = first
    //     // pub order: ParserOrder,
    //     pub type_index: usize,
    //     /// The actual parser function
    //     pub try_parse: fn(Token) -> TokenParsingResult<dyn TextElement, Token>,
    //     // pub from_narration: fn(Narration, &ParseContext) -> (usize, *mut ()),
    //     pub from_narration: fn(Narration, &ParseContext) -> (usize, *mut ()),
    //     pub drop_fn: unsafe fn(*mut ()),
    //     // pub clone_fn: unsafe fn(*mut ()) -> *mut (),
    // }

/// Parser with explicit ordering hint
pub struct Parser {
    pub name: &'static str,
    /// Ordering hint: Fallback = last, Normal = middle, Priority = first
    // pub order: ParserOrder,
    pub from_token: fn(&Token) -> TokenParsingResult<Box<dyn TextElementAuto>>,
    pub from_narration: fn(Narration, &ParseContext) -> Box<dyn TextElementAuto>,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord)]
pub enum ParserOrder {
    /// Will be tried first (e.g., very specific patterns)
    Priority = 0,
    /// Default ordering (most parsers)
    Normal = 1,
    /// Fallback parsers that match broadly (e.g., Narration)
    Fallback = 2,
}

/// The distributed slice that collects all parsers at link time
#[distributed_slice]
pub static TEXT_ELEMENT_PARSERS: [Parser] = [..];