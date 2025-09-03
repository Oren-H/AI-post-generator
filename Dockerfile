# Use Python 3.13 slim image to meet audioop-lts requirements
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies for PDF processing and image handling
RUN apt-get update && apt-get install -y \
    --no-install-recommends \
    gcc fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port for Gradio UI
EXPOSE 7860

# Default command runs the Gradio UI
# To run CLI instead, override with: docker run -it <image> python -m src.main
CMD ["python", "-m", "src.gui"]
