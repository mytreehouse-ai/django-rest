#!/bin/bash
set -e

psql -U postgres -d django -c 'CREATE EXTENSION IF NOT EXISTS vector;'
