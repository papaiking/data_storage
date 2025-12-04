# Use the official Python image as the base image
# We use a slim version to keep the image size down
FROM python:3.12.0-slim as builder

# Set environment variables for the application
ENV PYTHONUNBUFFERED 1
ENV POETRY_VIRTUALENVS_CREATE false
ENV VIRTUAL_ENV="/usr/local"

# Set the working directory inside the container
WORKDIR /app

# 1. Install dependencies
# Copy only the requirements file first to leverage Docker layer caching.
# If requirements.txt doesn't change, this step is skipped on subsequent builds.
COPY requirements.txt .

# Install dependencies, ensuring 'uvicorn' and 'gunicorn' are in requirements.txt
# (You might need to add 'gunicorn' and 'uvicorn[standard]' if not already present)
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy the rest of the application code
# This step only runs if other files have changed.
COPY . .

# Ensure the start script is executable
RUN chmod +x /app/start.sh

# 3. Expose the port
# The application will run on this port inside the container
EXPOSE 8000

# 4. Define the command to run the application in production
# This command executes the robust Gunicorn + Uvicorn setup script.
# Configuration is handled via environment variables passed when running the container (e.g., SECRET_KEY, DB_USER, etc.)
CMD ["./start.sh"]