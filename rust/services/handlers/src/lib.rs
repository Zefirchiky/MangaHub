#![feature(custom_test_frameworks)]
#![feature(test)]
#![test_runner(custom_test_runner)]

extern crate test;

use std::fs;

use test::{TestDescAndFn, test_main_static};

pub mod file;

// static FILE_NAME_EXT: fn(&str) -> String = |ext| format!("dis/pls.{}", ext);
// static FILE_NAME: &str = "dis/pls";

pub fn custom_test_runner(tests: &[&TestDescAndFn]) {
    test_main_static(tests);
    _ = fs::remove_dir_all("dis");
}

// mod md_handler;
// pub use md_handler::{MdHandler, TemporaryMdHandler};
