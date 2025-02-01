#!/bin/bash

# Project configuration
export PROJECT_ID="hack-at-davidson25"  # Replace with your actual project ID
export REGION="us-east1"
export RUNTIME="python39"

# Service account configuration
export SERVICE_ACCOUNT_NAME="ai-query-service-account"
export SERVICE_ACCOUNT_EMAIL="$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"

# Function configuration
export MEMORY="256Mi"  # Updated to use Mi suffix for Gen2
export TIMEOUT="30s"   # Reduced timeout for free tier
export MIN_INSTANCES="0"  # Scale to zero when not in use
export MAX_INSTANCES="10" # Limited max instances to control costs
export INGRESS_SETTINGS="all"  # Changed from allow-all to all

# Required APIs (including Artifact Registry for Cloud Functions Gen2 and Vertex AI)
export REQUIRED_APIS=(
    "cloudfunctions.googleapis.com"
    "cloudbuild.googleapis.com"
    "artifactregistry.googleapis.com"
    "run.googleapis.com"
    "aiplatform.googleapis.com"
)
