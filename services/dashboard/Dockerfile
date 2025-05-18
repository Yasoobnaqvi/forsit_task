FROM python:3.9-slim

RUN mkdir -p /app

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 6061

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "6061", "--reload"]
