FROM ubuntu:22.04

# Install system dependencies including FFmpeg
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libavcodec-extra \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

# Copy application code
COPY . .

# Create directories for file uploads and conversions
RUN mkdir -p uploads converted

# Expose port
EXPOSE 8000

# Run the application
CMD ["python3", "app.py"]
