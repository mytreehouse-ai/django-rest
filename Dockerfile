FROM python:3.11-slim

# Install system dependencies required for the project
# Including 'git' to ensure successful installation of dependencies from git repositories
RUN apt-get update && apt-get install -y --no-install-recommends git

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PATH="/home/appuser/.local/bin:${PATH}"

# Set the working directory
WORKDIR /app

# Create a non-root user and ensure /app directory is owned by appuser
RUN useradd -m appuser && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Copy the requirements file and install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application with appropriate permissions
COPY --chown=appuser:appuser . /app/

# Expose port 8000 (or the port your Django app is running on)
EXPOSE 8000

# Command to run the Django server
CMD sh -c "\
    python manage.py makemigrations --noinput && \
    python manage.py migrate --noinput && \
    gunicorn mytreehouse.wsgi:application --bind 0.0.0.0:8000"
