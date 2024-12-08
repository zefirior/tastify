FROM python:3.12.2

WORKDIR /app

# Install required dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    build-essential \
    && wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash \
    && . /root/.nvm/nvm.sh \
    && nvm install 22.8.0 \
    && nvm use 22.8.0 \
    && nvm alias default 22.8.0

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip freeze

COPY assets assets
COPY rxconfig.py rxconfig.py
COPY alembic alembic
COPY scripts scripts
COPY tastify tastify

RUN reflex db migrate

ENV PYTHONPATH=/app
CMD bash /app/scripts/run.sh
