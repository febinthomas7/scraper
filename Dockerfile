# Use slim Python base
FROM python:3.9-slim

WORKDIR /app

# Install only minimal system dependencies for Chromium
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    wget \
    libnss3 \
    libxkbcommon0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxshmfence1 \
    libgtk-3-0 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and only Chromium browser
RUN pip install playwright && playwright install chromium

# Copy app code
COPY . .

EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
