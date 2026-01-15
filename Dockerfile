FROM python:3.13-slim-bookworm

WORKDIR /app

COPY . .

RUN pip install .

RUN adduser --disabled-password appuser
USER appuser

EXPOSE 8000

CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000"]