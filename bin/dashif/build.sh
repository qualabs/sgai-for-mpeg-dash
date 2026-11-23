#!/usr/bin/env bash
# Build the pinned DASH-IF conformance tool image (bin/dashif/UPSTREAM).
# Verifies the tag resolves to the pinned commit before building, and caps the
# build's memory and CPU.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
kv() { sed -n "s/^$1=//p" "$HERE/UPSTREAM"; }
REPO="$(kv repo)"; TAG="$(kv tag)"; COMMIT="$(kv commit)"
IMAGE="${SGAI_DASHIF_IMAGE:-$(kv image)}"
MEM="${SGAI_DASHIF_BUILD_MEMORY:-3g}"
CPUS="${SGAI_DASHIF_BUILD_CPUS:-1}"

# The clone is ~100 MB: a 0700 directory on disk, removed on exit.
mkdir -p "$HOME/.cache/cto-tmp"
SCRATCH="$(mktemp -d "$HOME/.cache/cto-tmp/sgai-dashif-build-XXXXXX")"
chmod 700 "$SCRATCH"
trap 'rm -rf "$SCRATCH"' EXIT

echo "=== cloning $REPO @ $TAG ==="
git clone -q --depth 1 --branch "$TAG" "$REPO" "$SCRATCH/src"
got="$(git -C "$SCRATCH/src" rev-parse HEAD)"
[ "$got" = "$COMMIT" ] || { echo "FAIL: tag $TAG is at $got, UPSTREAM pins $COMMIT" >&2; exit 1; }
echo "commit verified: $got"

cp "$HERE/Dockerfile" "$SCRATCH/src/Dockerfile.sgai"
cp "$HERE/w3c-catalog.xml" "$SCRATCH/src/w3c-catalog.xml"
DOCKER_BUILDKIT=0 docker build \
  --memory "$MEM" --memory-swap "$MEM" \
  --cpu-period 100000 --cpu-quota "$((CPUS * 100000))" \
  --label "org.opencontainers.image.revision=$COMMIT" \
  -f "$SCRATCH/src/Dockerfile.sgai" -t "$IMAGE" "$SCRATCH/src"
echo "built $IMAGE from $COMMIT"
