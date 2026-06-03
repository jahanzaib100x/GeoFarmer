# Use official lightweight Python image
FROM python:3.10-slim

# Set environment system variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# Set working directory inside container
WORKDIR /app

# Install libgomp1 (required for onnxruntime CPU execution)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies manifest
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source files
COPY . .

# Create directory for image diagnostic caching
RUN mkdir -p temp_uploads && chmod 777 temp_uploads

# Expose server listener port
EXPOSE 8000

# Start FastAPI server using uvicorn
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
