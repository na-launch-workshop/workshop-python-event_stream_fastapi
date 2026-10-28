# Not built from here. The price-api sidecar in Task 6 runs workspace-images/electricity-price-api,
# which the cluster builds from cluster/workspace-images/electricity-price-api/ in
# ocp-dev-days-rdshw-gitops — a copy of this price_api.py and Dockerfile. Change both together,
# then rebuild with: oc start-build electricity-price-api -n workspace-images
FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn
COPY price_api.py .
EXPOSE 5000
CMD ["python", "price_api.py"]
