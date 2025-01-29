FROM ghcr.io/astral-sh/uv:python3.12-alpine
WORKDIR /app
ADD main.py /app/
ADD pyproject.toml /app/
COPY src /app/src/
CMD ["uv", "run", "main.py", "-s"]