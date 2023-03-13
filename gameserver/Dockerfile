# Choose a base image
FROM redis:7.0.9-bullseye

# Set the working directory
WORKDIR /app

# Copy the application code
COPY . /app
# Install any necessary dependencies
# RUN pip install --no-cache-dir \
#     && apt-get update \
#     && apt-get install -y --no-install-recommends \
#        gcc \
#     && rm -rf /var/lib/apt/lists/*
RUN apt update \
    && apt-get install -y \
    python3 \
    python3-pip
#RUN apt-get install redis-server -y
#RUN service redis start
#RUN apt install python3 -y
RUN pip3 install redis
# Expose any necessary ports
EXPOSE 5050 5051 5052

# Define the command to run the application
CMD ["python3", "game_server.py"]