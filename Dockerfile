# Use a slim Python 3.9 image as the base
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Install system dependencies for Playwright's browsers
RUN apt-get update -y && apt-get install -y --no-install-recommends

libnss3

libnss3-dev

libfontconfig1

libgconf-2-4

libgdk-pixbuf2.0-0

libxkbcommon0

libxkbfile1

libxss1

libgbm1

libdrm2

libvulkan1

libexpat1

libwebp6

libpng16-16

libjpeg-turbo8

libtiff5

libharfbuzz0b

libglib2.0-0

libgdk-pixbuf2.0-0

libxcb1

libxrender1

libxi6

libxtst6

libxrandr2

libcups2

libfreetype6

libwoff1

libsnappy1v5

liblzma5

libgconf-2-4

libgtk-4-dev

libgraphene-1.0-dev

libgstreamer1.0-dev

libgstreamer-plugins-base1.0-dev

libenchant-2-dev

libsecret-1-dev

libmanette-0.2-dev

libgles2-mesa-dev

# Copy the requirements file and install Python packages
COPY requirements.txt . RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright's browser binaries
RUN playwright install --with-deps chromium

# Copy the rest of your application code
COPY . .

# Expose the port FastAPI runs on
EXPOSE 8000

# Command to run the application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]