FROM python:3.11-slim as build
LABEL Author="Milco Numan" REPO="https://github.com/mnuman/sudocku" Language="Python"
COPY ./app app
WORKDIR /app
RUN set -ex \
    # Create a non-root user
    && addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --gid 1001 --no-create-home appuser \
    # Install dependencies
    && pip install -r requirements.txt --no-cache-dir
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
USER appuser
