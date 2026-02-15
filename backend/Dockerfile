# Base Image
FROM python:3.11-slim

# Set Working Directory
WORKDIR /app

# Set Environment Variables 
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy Project
COPY . /app/