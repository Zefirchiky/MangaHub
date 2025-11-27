use std::{any::Any, fmt::Debug};

use derive_more::{Deref, DerefMut, From};

use crate::novel::{Context, Token};

pub trait WordTrait: Any + Sync + Sync + Debug {
    fn try_from_token(token: Token, ctx: Context) -> Self;
}

#[allow(dead_code)]
pub struct Name {
    pub character: String,
    pub has_name: bool,
    pub has_surname: bool,
    pub candidate_names: Vec<String>,
    pub candidate_surnames: Vec<String>,
}

#[derive(Debug, Default, From, Deref, DerefMut)]
#[from(forward)]
#[allow(dead_code)]
pub struct Word {
    #[deref]
    #[deref_mut]
    pub word: Token,
    pub suggestions: Vec<String>,
}
