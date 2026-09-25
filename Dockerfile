FROM python:3.12-slim
WORKDIR /app
COPY . .
CMD ["python","secure_gateway.py"]
