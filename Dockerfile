# Use a base image with Debian or Ubuntu support
FROM python:3.10-slim

# Set environment variables for non-interactive install
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies for headless Chromium
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

# Copy your app files
COPY . /app

# Set environment variables for Chromium and Chromedriver
ENV CHROMIUM_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_BIN=/usr/bin/chromium-driver

# Run your Python script
CMD ["python", "hqb.py"]
