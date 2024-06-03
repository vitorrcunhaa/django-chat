# Pull base image
FROM python:3.9

# Set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y netcat-openbsd && apt-get install redis-server -y

# Initialize redis server
RUN service redis-server start

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Install testing dependencies
RUN pip install pytest pytest-django channels-redis

# Copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Copy project
COPY . /app/

# Run entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]