FROM python:3.14 AS builder

COPY requirements.txt .

RUN pip install --user -r requirements.txt

FROM python:3.14-slim

WORKDIR /app

ENV PATH=/root/.local/bin:$PATH

COPY --from=builder /root/.local /root/.local

COPY ./zip /app

EXPOSE 8000

CMD ["fastapi", "run", "main.py", "--port", "8000"]