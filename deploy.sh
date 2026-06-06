#!/bin/bash
set -e

# --- Config ---
source .env
REMOTE_DIR="/root"
LOCAL_DIR="."


# --- Sync ---
echo "Syncing files..."
sshpass -p "$SSH_PASSWORD" rsync -avz --exclude='venv/' --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='.env.local' --exclude='logs/' \
  "$LOCAL_DIR/" "$REMOTE_USER@$REMOTE_HOST:/$REMOTE_DIR/"

# --- Build & Up ---
echo "Building and starting containers..."

BUILD_FLAGS=""

# If the first argument is "cache", remove the flag (meaning it WILL use cache)
if [ "$1" == "--no-cache" ]; then
    BUILD_FLAGS="--no-cache"
    echo "Building WITHOUT cache..."
else
    echo "Building WITH cache..."
fi

sshpass -p "$SSH_PASSWORD" ssh "$REMOTE_USER@$REMOTE_HOST" "cd $REMOTE_DIR && chmod +x backup.sh && docker compose down && sudo docker compose build $BUILD_FLAGS && docker compose up -d"

echo "Done."


# set -e

# source .env

# # Configuration
# IMAGE_NAME="diabetes-app"
# IMAGE_TAG="latest"
# REMOTE_DIR="/root/diabetes-application"
# LOCAL_DIR="."
# TAR_FILE="./${IMAGE_NAME}.tar"

# echo "Removing old images..."
# sudo docker rmi diabetes-application-web:latest diabetes-application-celery:latest 2>/dev/null || true

# BUILD_FLAGS=""

# # If the first argument is "no-cache", remove the flag (meaning it WILL use cache)
# if [ "$1" == "--no-cache" ]; then
#     BUILD_FLAGS="--no-cache"
#     echo "Building WITHOUT cache..."
# else
#     echo "Building WITH cache..."
# fi

# sudo docker compose build $BUILD_FLAGS

# echo "Checking built images..."
# sudo docker images | grep diabetes-application

# echo "Saving images to tar file..."
# sudo docker save diabetes-application-web:latest diabetes-application-celery:latest > "$TAR_FILE"

# echo "Changing permissions..."
# sudo chmod 644 "$TAR_FILE"

# echo "Verifying tar file..."
# ls -lh "$TAR_FILE"

# echo "Syncing files..."
# rsync -avz --exclude='venv/' --exclude='.git' --exclude='__pycache__' \
#   --exclude='*.pyc' --exclude='.env.local' --exclude='logs/' --exclude='*.tar' \
#   "$LOCAL_DIR/" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/"

# echo "Transferring Docker images..."
# rsync -avz --progress "$TAR_FILE" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/${IMAGE_NAME}.tar"

# echo "Loading images and starting containers on server..."
# ssh "$REMOTE_USER@$REMOTE_HOST" << EOF
# cd $REMOTE_DIR
# docker load -i ${IMAGE_NAME}.tar
# rm ${IMAGE_NAME}.tar
# docker compose down
# docker compose up -d
# EOF

# echo "Cleaning up..."
# sudo rm "$TAR_FILE"

# echo "Done."
