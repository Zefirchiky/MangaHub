FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml .
RUN uv sync
# RUN uv add pyinstaller
# RUN pyinstaller --version

# WORKDIR /mangahub
# COPY . .

# WORKDIR /
# RUN pyinstaller --onefile -w --name mangahub main.py

CMD ["uv", "run", "mangahub/main.py"]
