FROM python:3.11-slim

# Install system dependencies required for the project
# Including 'git' to ensure successful installation of dependencies from git repositories
RUN apt-get update && apt-get install -y --no-install-recommends git

ARG RUN_MODE

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
CMD if [ "$RUN_MODE" = "api-gateway" ]; then \
        sh -c "python manage.py makemigrations --noinput && \
               python manage.py migrate --noinput && \
               gunicorn mytreehouse.wsgi:application --bind 0.0.0.0:8000;"; \
    elif [ "$RUN_MODE" = "celery-beat" ]; then \
        sh -c "celery -A mytreehouse beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler"; \
    elif [ "$RUN_MODE" = "celery-worker" ]; then \
        sh -c "celery -A mytreehouse worker -l INFO -E --concurrency=2"; \
    fi
