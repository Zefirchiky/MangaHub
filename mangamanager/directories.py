import os

STD_DIR = os.getcwd()

def create_directory(directory: str) -> None:
    if not os.path.exists(directory):
        os.makedirs(directory)

def create_directories(directories: list) -> None:
    for directory in directories:
        create_directory(directory)