#!/bin/bash

# Configuration
PROJECT_ID="hack-at-davidson25"
BUCKET_NAME="pine-config"
REGION="us-east1"

echo "🚀 Uploading Pine configuration..."

# Create the bucket if it doesn't exist
gsutil mb -l ${REGION} gs://${BUCKET_NAME} || true

# Upload the configuration file
echo "📤 Uploading configuration file..."
gsutil cp pine_config.txt "gs://${BUCKET_NAME}/pine_config.txt"

# Upload the business directory
echo "📤 Uploading business directory..."
gsutil cp lknbusiness-rolodex.html "gs://${BUCKET_NAME}/lknbusiness-rolodex.html"

# Set public read access
gsutil acl ch -u AllUsers:R "gs://${BUCKET_NAME}/pine_config.txt"
gsutil acl ch -u AllUsers:R "gs://${BUCKET_NAME}/lknbusiness-rolodex.html"

echo "✅ Configuration and business directory uploaded successfully!"
echo "📍 Configuration location: gs://${BUCKET_NAME}/pine_config.txt"
