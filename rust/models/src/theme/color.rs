use std::str::FromStr;

use derive_more::{Deref, DerefMut, From};
use palette::{IntoColor, Srgb};
use serde::{Deserialize, Serialize};

#[derive(Debug, Deref, From, DerefMut, Serialize, Deserialize)]
pub struct Color(pub palette::Alpha<palette::rgb::Srgb, f32>);

impl Color {
    pub fn from_hsla(hue: f32, saturation: f32, lightness: f32, alpha: f32) -> Self {
        Self(palette::hsl::Hsla::new_srgb(hue, saturation, lightness, alpha).into_color())
    }

    pub fn from_hsl(hue: f32, saturation: f32, lightness: f32) -> Self {
        Self::from_hsla(hue, saturation, lightness, 100.)
    }

    pub fn from_rgba(red: f32, green: f32, blue: f32, alpha: f32) -> Self {
        Self(palette::rgb::Rgba::new(red, green, blue, alpha))
    }

    pub fn from_rgb(red: f32, green: f32, blue: f32) -> Self {
        Self::from_rgba(red, green, blue, 100.)
    }

    pub fn from_hex(hex: &String) -> Self {
        Self(palette::rgb::Rgba::from_str(hex).expect(&format!("Wrong string: {hex}")).into())
    }

    pub fn as_hex(&self) -> String {
        format!("#{:x}", Srgb::<u8>::from_linear(self.0.color.into()))
    }
}
