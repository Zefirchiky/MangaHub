#![feature(custom_test_frameworks)]
#![feature(test)]
#![test_runner(custom_test_runner)]

extern crate test;

use std::fs;

use test::{test_main_static, TestDescAndFn};

// static FILE_NAME_EXT: fn(&str) -> String = |ext| format!("dis/pls.{}", ext);
// static FILE_NAME: &str = "dis/pls";

pub fn custom_test_runner(tests: &[&TestDescAndFn]) {
    test_main_static(tests);
    _ = fs::remove_dir_all("dis");
}

mod file_handler;
pub use file_handler::{FileHandler, Handler, Temporary};

mod json_handler;
pub use json_handler::{JsonHandler};

mod md_handler;
pub use md_handler::{MdHandler, TemporaryMdHandler};