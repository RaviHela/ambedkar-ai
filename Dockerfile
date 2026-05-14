FROM python:3.10-slim
WORKDIR /app
COPY backend/requirements_light.txt .
RUN pip install --no-cache-dir -r requirements_light.txt
COPY backend/ .
COPY webapp/ ./webapp/
ENV PYTHONPATH=/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
