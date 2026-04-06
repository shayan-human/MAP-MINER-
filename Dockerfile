FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for Playwright (Chromium)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY turbo/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and Chromium
RUN pip install playwright && playwright install chromium

# Copy project files
COPY . .

# Create directories
RUN mkdir -p outputs gmapsdata

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "turbo.server:app", "--host", "0.0.0.0", "--port", "8000"]
