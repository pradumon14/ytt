FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install ytt package
RUN pip install --no-cache-dir -e .

ENTRYPOINT ["ytt"]
CMD ["--help"]
