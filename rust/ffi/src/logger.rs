use std::io::Write;

use log::Level;
use owo_colors::OwoColorize;

pub fn init_logger() {
    env_logger::Builder::from_default_env()
        .filter_level(log::LevelFilter::Warn)
        .format(|buf, record| {
            let level = record.level();
            let level_text = match record.level() {
                Level::Error => level.red().into_styled(),
                Level::Warn => level.bright_yellow().into_styled(),
                Level::Info => level.blue().into_styled(),
                Level::Debug => level.dimmed().into_styled(),
                Level::Trace => level.dimmed().into_styled(),
            };

            match record.line() {
                Some(l) => writeln!(
                    buf,
                    "[{}] {}::{}: {}",
                    level_text,
                    record.target().purple(),
                    l.purple(),
                    record.args(),
                ),
                None => writeln!(
                    buf,
                    "[{}] {}: {}",
                    level_text,
                    record.target().purple(),
                    record.args(),
                ),
            }
        })
        .init();
}
