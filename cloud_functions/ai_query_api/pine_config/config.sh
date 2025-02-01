#!/bin/bash

# Configuration
PROJECT_ID="hack-at-davidson25"
BUCKET_NAME="pine-config"
REGION="us-east1"

echo "🚀 Uploading Pine configuration..."

# Create bucket if it doesn't exist
if ! gsutil ls -b "gs://${BUCKET_NAME}" &>/dev/null; then
    echo "📦 Creating bucket gs://${BUCKET_NAME}..."
    gsutil mb -l ${REGION} "gs://${BUCKET_NAME}"
fi

# Upload configuration file
echo "📤 Uploading configuration file..."
gsutil cp pine_config.txt "gs://${BUCKET_NAME}/"

echo "✅ Configuration uploaded successfully!"
echo "📍 Configuration location: gs://${BUCKET_NAME}/pine_config.txt"
