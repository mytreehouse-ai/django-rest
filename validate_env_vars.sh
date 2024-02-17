#!/bin/sh
# validate_env_vars.sh

# Check each required variable
required_vars="NODE_ENV"

for var in $required_vars; do
    if [ -z "$(eval echo \$$var)" ]; then
        echo "Error: Environment variable $var is not set."
        exit 1
    fi
done

echo "All required environment variables are set."