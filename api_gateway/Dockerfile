# Base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the app files
COPY api_gateway.py .
COPY routing_config.yaml .

# Expose the application port
EXPOSE 5000

# Run the application
CMD ["python", "api_gateway.py"]
