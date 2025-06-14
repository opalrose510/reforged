# Use Python 3.11 as the base image
FROM python:3.11-slim

# Create a non-root user
RUN useradd -m -s /bin/bash ubuntu

# Set working directory to user's home
WORKDIR /home/ubuntu

# Copy only requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER ubuntu

# Command to run the background agent
CMD ["python", "play.py", "saves/save.json"] 