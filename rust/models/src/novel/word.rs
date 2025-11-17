use std::{any::Any, fmt::Debug};

use derive_more::{Deref, DerefMut, From};

use crate::novel::{Context, Token};

pub trait WordTrait: Any + Sync + Sync + Debug {
    fn try_from_token(token: Token, ctx: Context) -> Self;
}

pub struct Name {
    character: String,
    has_name: bool,
    has_surname: bool,
    candidate_names: Vec<String>,
    candidate_surnames: Vec<String>,
}

#[derive(Debug, Default, From, Deref, DerefMut)]
#[from(forward)]
pub struct Word {
    #[deref]
    #[deref_mut]
    pub word: Token,
    pub suggestions: Vec<String>,
}
