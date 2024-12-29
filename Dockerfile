# Use an official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    pkg-config \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    && apt-get clean

# Create and set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose port and run server
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "arieshelby.wsgi:application"]
