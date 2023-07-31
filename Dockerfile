# Björn van Dijkman
# https://medium.com/vantageai/how-to-make-your-python-docker-images-secure-fast-small-b3a6870373a0
FROM python:3.11-slim as build
COPY ./app app
WORKDIR /app
RUN set -ex \
    # Create a non-root user
    && addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --gid 1001 --no-create-home appuser \
    # Upgrade the package index and install security upgrades
    && apt-get update \
    && apt-get upgrade -y \
    # Install dependencies
    && pip install -r requirements.txt \
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
USER appuser
