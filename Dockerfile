FROM python:3.10-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    chromium-browser \
    chromium-chromedriver \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt

# Set environment variables for Chromium
ENV CHROMIUM_BIN=/usr/bin/chromium-browser
ENV CHROMEDRIVER_BIN=/usr/bin/chromedriver

# Copy the application code
COPY . /app

# Run the Python script
CMD ["python", "hqb.py"]
