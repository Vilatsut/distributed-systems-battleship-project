# Choose a base image
FROM python:3.9-slim-buster

# Set the working directory
WORKDIR /app

# Copy the application code
COPY loadbalancer.py loadbalancer.py

RUN pip3 install redis
# Expose any necessary ports
EXPOSE 16432

# Define the command to run the application
CMD ["python3", "loadbalancer.py"]