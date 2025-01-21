FROM python:3.9-slim


WORKDIR /app

COPY config.ini /app/config.ini

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5003

ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Comando para rodar a aplicação
CMD ["flask", "run"]