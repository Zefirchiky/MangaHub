FROM python:3.13-slim AS windows-builder

WORKDIR /

COPY pyproject.toml .
RUN pip install uv
RUN uv sync
RUN uv add pyinstaller
RUN pyinstaller --version

WORKDIR /mangahub
COPY . .

WORKDIR /
RUN pyinstaller --onefile -w --name mangahub main.py
