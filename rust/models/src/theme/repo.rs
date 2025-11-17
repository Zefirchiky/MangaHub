use uuid::Uuid;

use crate::{repos::RepoBase, theme::Theme};

pub type Repo = RepoBase<Uuid, Theme>;