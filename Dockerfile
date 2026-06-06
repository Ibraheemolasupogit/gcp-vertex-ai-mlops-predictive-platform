FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/src
ENV PORT=8080

WORKDIR /app

RUN groupadd --system appuser && useradd --system --gid appuser appuser

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY models/predictive_maintenance_model.joblib ./models/predictive_maintenance_model.joblib
COPY models/model_metadata.json ./models/model_metadata.json
COPY models/README.md ./models/README.md

EXPOSE 8080

USER appuser

CMD ["sh", "-c", "uvicorn vertex_mlops_platform.serving.api:app --host 0.0.0.0 --port ${PORT:-8080}"]
