# Use official Python 3.10 slim image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=new_dashboard/app.py
ENV FLASK_ENV=production

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir psycopg2-binary gunicorn eventlet

# Copy the rest of the application
COPY . .

# Expose port (Render sets PORT env variable)
EXPOSE 10000

# Start application using Gunicorn with Eventlet worker for SocketIO support
CMD gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:$PORT new_dashboard.app:app
