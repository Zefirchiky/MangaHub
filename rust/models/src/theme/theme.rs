use std::{path::Path};

use handlers::file::{Json, ModelFileTrait, ModelJsonIoError};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::theme::Color;

#[derive(Debug, thiserror::Error)]
pub enum ThemeIoError {
    #[error("No theme file")]
    NoFile,
    #[error("Serder Error: {0}")]
    SerdeError(#[from] ModelJsonIoError),
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Theme {
    #[serde(skip)]
    file: Option<Json>,
    id: Uuid,
    name: String,

    pub bg_dark:    Option<Color>,
    pub bg:         Option<Color>,
    pub bg_light:   Option<Color>,
    pub text:       Option<Color>,
    pub text_muted: Option<Color>,
    pub border:     Option<Color>,
    pub hightlight: Option<Color>,

    pub error:      Option<Color>,
    pub warning:    Option<Color>,
    pub success:    Option<Color>,
    pub info:       Option<Color>,
}

impl Theme {
    pub fn new(name: String, file: Option<impl AsRef<Path>>) -> Self {
        Self {
            file: file.and_then(|f| Some(Json::new(f))),
            name,
            ..Default::default()
        }
    }

    pub fn load(&mut self) -> Result<Self, ThemeIoError> {
        if let Some(f) = &self.file {
            return Ok(f.load_model::<Theme>()?);
        }
        Err(ThemeIoError::NoFile)
    }
    
    pub fn save(&self, file: Option<Json>) -> Result<(), ThemeIoError> {
        if let Some(f) = &file {
            Ok(f.save_model(self)?)
        } else if let Some(f) = &self.file {
            Ok(f.save_model(self)?)
        } else {
            Err(ThemeIoError::NoFile)
        }
    }
}

impl Default for Theme {
    fn default() -> Self {
        Self {
            file: None,
            id: Uuid::new_v4(),
            name: String::new(),
            bg_dark:    Some(Color::from_hsl(0., 0., 0.00)),
            bg:         Some(Color::from_hsl(0., 0., 0.05)),
            bg_light:   Some(Color::from_hsl(0., 0., 0.10)),
            text:       Some(Color::from_hsl(0., 0., 0.95)),
            text_muted: Some(Color::from_hsl(0., 0., 0.70)),
            border:     Some(Color::from_hsl(0., 0., 0.30)),
            hightlight: Some(Color::from_hsl(0., 0., 0.60)),
            error:      Some(Color::from_hsla(007., 0.89, 0.66, 50.)),
            warning:    Some(Color::from_hsla(054., 1.00, 0.25, 50.)),
            success:    Some(Color::from_hsla(162., 1.00, 0.29, 50.)),
            info:       Some(Color::from_hsla(217., 1.00, 0.69, 50.)),
        }
    }
}