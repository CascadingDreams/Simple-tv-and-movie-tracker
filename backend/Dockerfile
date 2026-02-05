FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y postgresql-client

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x migration_setup.sh

CMD ["./migration_setup.sh"]