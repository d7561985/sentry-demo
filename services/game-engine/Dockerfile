FROM python:3.8-slim

WORKDIR /app

# Install build dependencies for psutil
RUN apt-get update && apt-get install -y gcc python3-dev && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8082

# Run the application
CMD ["python", "main.py"]