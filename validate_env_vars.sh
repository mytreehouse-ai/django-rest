#!/bin/sh
# validate_env_vars.sh

# Load environment variables from .env file
if [ -f .env ]; then
    # Read .env file line by line and export variables
    while IFS= read -r line || [ -n "$line" ]; do
        # Ignore lines starting with #
        if ! echo "$line" | grep -q "^\s*#"; then
            export "$line"
        fi
    done < .env
else
    echo "Error: .env file not found."
    exit 1
fi

# Check each required variable
required_vars="NODE_ENV DJANGO_SECRET_KEY DJANGO_API_URL \
CORS_ALLOWED_ORIGINS CSRF_TRUSTED_ORIGINS DJANGO_ALLOWED_HOSTS \
MONGODB_URI OPENAI_API_KEY POSTGRES_DATABASE POSTGRES_HOST \
POSTGRES_USERNAME POSTGRES_PASSWORD POSTGRES_PORT \
REDIS_CACHE_URL REDIS_PASSWORD REDIS_VM_IP_ADD \
SCRAPER_API_KEY POSTGRES_SSL_ON \
REDIS_SSL_ENABLED"

for var in $required_vars; do
    if [ -z "$(eval echo \$$var)" ]; then
        echo "Error: Environment variable $var is not set."
        exit 1
    fi
done

echo "All required environment variables are set."

# Unset all exported variables
for var in $required_vars; do
    unset "$var"
done