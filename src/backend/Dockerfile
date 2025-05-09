# Help from: https://github.com/cohere-ai/cohere-toolkit/blob/main/src/backend/Dockerfile

FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV PYTHONPATH=/workspace/src/

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

ENV VIRTUAL_ENV=/workspace/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV POETRY_VERSION 1.5.1

WORKDIR /workspace

# Copy dependency files to avoid cache invalidations
COPY pyproject.toml poetry.lock ./

COPY src/backend/ src/backend/

RUN pip install --no-cache-dir poetry==1.8.2 \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi


EXPOSE 8000

CMD ["poetry","run","uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
