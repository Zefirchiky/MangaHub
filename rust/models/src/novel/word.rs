use std::{any::Any, fmt::Debug};

use crate::novel::{Context, Token};

pub trait WordTrait: Any + Sync + Sync + Debug {
    fn try_from_token(token: Token, ctx: Context) -> Self;
}

struct Name {
    character: String,
    has_name: bool,
    has_surname: bool,
    candidate_names: Vec<String>,
    candidate_surnames: Vec<String>,
}

struct Word {
    word: Token,
    suggestions: Vec<String>,
}