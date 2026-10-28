# Published as quay.io/pknezevich/electricity-price-api (public); workspaces pull it in Task 6.
# Rebuild after changing price_api.py (cluster workers are x86):
#   podman build --platform linux/amd64 -t quay.io/pknezevich/electricity-price-api:v1 sidecar
#   podman push quay.io/pknezevich/electricity-price-api:v1
FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn
COPY price_api.py .
EXPOSE 5000
CMD ["python", "price_api.py"]
