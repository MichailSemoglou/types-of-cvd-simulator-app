# CVD Simulator Docker Image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the package
COPY src/ ./src/
COPY pyproject.toml .
COPY README.md .

# Install the package
RUN pip install -e .

# Create output directory
RUN mkdir -p /outputs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV CVD_SIMULATOR_OUTPUT_DIRECTORY=/outputs

# Default command
ENTRYPOINT ["cvd-simulator"]
CMD ["--help"]
