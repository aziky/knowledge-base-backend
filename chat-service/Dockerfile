# Backend Dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     gcc \
#     && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirement.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirement.txt

# Copy application code
COPY . .

# Copy rest of the source code
COPY . .

# Expose port
EXPOSE 7075

# Run app
CMD ["python", "main.py"]
