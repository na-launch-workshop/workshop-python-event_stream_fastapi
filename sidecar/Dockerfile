FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn
COPY price_api.py .
EXPOSE 5000
CMD ["python", "price_api.py"]
