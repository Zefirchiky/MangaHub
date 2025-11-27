use serde::{Deserialize, Serialize};

use crate::file::{File, Json, Md};

#[derive(Debug, Serialize, Deserialize)]
pub enum FileTypes {
    File(File),
    Json(Json),
    Md(Md),
}
