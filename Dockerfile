FROM python:3.14 as builder

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --user --no-cache-dir --upgrade -r /app/requirements.txt

FROM python:3.14-slim as runtime

WORKDIR /app

COPY .env /app/.env
COPY --from=builder /root/.local /root/.local

ENV PATH=/root/.local/bin:$PATH

COPY . /app
COPY credential.json ./credential.json

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
