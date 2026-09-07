FROM python:3.12

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r /app/requirements.txt

EXPOSE 8000

COPY ./zip /app/zip

CMD ["fastapi", "run", "zip/main.py", "--port", "8000"]