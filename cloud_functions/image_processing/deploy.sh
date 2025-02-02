#!/bin/bash

# Exit on error
set -e

# Function name
FUNCTION_NAME="image_processing"

# Region
REGION="us-east1"

# Project ID
PROJECT_ID="hack-at-davidson25"

# Service account that will be allowed to invoke the function
INVOKER_SA="ai-query-service-account@${PROJECT_ID}.iam.gserviceaccount.com"

echo "🚀 Deploying $FUNCTION_NAME..."

# Deploy the function with authentication required
gcloud functions deploy $FUNCTION_NAME \
  --gen2 \
  --region=$REGION \
  --runtime=python311 \
  --source=. \
  --entry-point=handle_request \
  --trigger-http \
  --no-allow-unauthenticated

# Set IAM policy to allow only the ai-query-service-account to invoke the function
echo "🔒 Setting IAM policy..."
gcloud functions add-invoker-policy-binding $FUNCTION_NAME \
  --region=$REGION \
  --member="serviceAccount:${INVOKER_SA}"

echo "✅ Deployment complete!"
