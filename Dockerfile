# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . /app/

# Expose port
EXPOSE 8000

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations and start server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "arieshelby.wsgi:application"]
