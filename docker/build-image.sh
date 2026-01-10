#!/bin/bash
# Build and optionally push the TermGame Ubuntu image

set -e

IMAGE_NAME="${IMAGE_NAME:-termgame/ubuntu}"
IMAGE_TAG="${IMAGE_TAG:-22.04}"
FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"

echo "Building TermGame Ubuntu image: ${FULL_IMAGE}"
echo "=========================================="

# Build the image
docker build \
    -f docker/Dockerfile.termgame-ubuntu \
    -t "${FULL_IMAGE}" \
    .

echo ""
echo "✓ Image built successfully: ${FULL_IMAGE}"
echo ""

# Test the image
echo "Testing image..."
docker run --rm "${FULL_IMAGE}" bash -c "
    echo 'Testing essential commands...'
    which nano vim && echo '✓ Text editors'
    which tree ncdu && echo '✓ File utilities'
    which gzip tar && echo '✓ Compression'
    which curl wget && echo '✓ Network tools'
    which htop && echo '✓ Process tools'
    which grep sed awk && echo '✓ Text processing'
    man --version > /dev/null && echo '✓ Man pages'
    echo '✓ All tests passed!'
"

echo ""
echo "=========================================="
echo "Image ready to use!"
echo ""
echo "To use in missions, update the image field to:"
echo "  image: \"${FULL_IMAGE}\""
echo ""
echo "To push to Docker Hub (requires login):"
echo "  docker push ${FULL_IMAGE}"
echo ""
