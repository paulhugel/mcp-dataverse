# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential gcc ffmpeg cmake git jq vim curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install uv
RUN pip install nemo_toolkit['asr']
#RUN pip install git+https://github.com/Dans-labs/pyDataverse@development#egg=pyDataverse

# Copy application code
COPY app /app/app
COPY utils /app/utils
COPY semantic_croissant /app/semantic_croissant
WORKDIR /app/semantic_croissant
RUN uv sync
WORKDIR /app
# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Run the application
CMD ["uv", "run", "semantic_croissant", "--transport", "sse", "--port", "8000"]
#CMD ["uvicorn", "semantic_croissant.server-min", "--host", "0.0.0.0", "--port", "8000", "--reload"]
