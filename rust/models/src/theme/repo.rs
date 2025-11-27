use handlers::file::Json;
use uuid::Uuid;

use crate::{repos::FileRepo, theme::Theme};

pub type Repo = FileRepo<Uuid, Theme, Json>;
