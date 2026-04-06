FROM python:3.10-slim

WORKDIR /app

# Install ALL system dependencies for Playwright (Chromium)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    # Core NSS libraries
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    # X11 libraries (fixes libXfixes.so.3 error)
    libxfixes3 \
    libx11-6 \
    libxcb1 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    # Graphics/Rendering
    libpango-1.0-0 \
    libcairo2 \
    libgbm1 \
    # Fonts
    libfontconfig1 \
    libfreetype6 \
    # Audio
    libasound2 \
    # Additional for stability
    libatspi2.0-0 \
    libdbus-1-3 \
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
