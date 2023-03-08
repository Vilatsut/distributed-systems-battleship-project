# Choose a base image
FROM python:3.9-slim-buster

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . /app
# Install any necessary dependencies
RUN pip install --no-cache-dir \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
    && rm -rf /var/lib/apt/lists/*

# Expose any necessary ports
EXPOSE 8000

# Define the command to run the application
CMD ["python", "game_server.py"]