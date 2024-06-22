FROM python:3.12.4
LABEL authors="joel"

ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.8.3

WORKDIR /app

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock /app/

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY . /app/

RUN python manage.py collectstatic --noinput --verbosity 2

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && poetry run gunicorn --bind 0.0.0.0:$PORT api_maribel.wsgi:application"]

