#!/usr/bin/env bash
# Put every *.mpd of a directory through the pinned DASH-IF conformance tool's
# MPD-level modules (Global Module + IOP MPD) and write one raw report per
# document, <name>.json, into the output directory. When the tool aborts on a
# document, <name>.json holds its error output instead of JSON.
#
#   bin/dashif/run.sh <in-dir> <out-dir>
#
# One container for the whole batch, memory and CPU capped, and NO network:
# the XSDs' w3.org imports are resolved from the image (see Dockerfile), and
# with network on the tool tries to fetch the example hosts the MPDs name and
# hangs on them (500 s curl timeout, no connect timeout). Each document gets a
# fresh `artisan` process, bounded by SGAI_DASHIF_DOC_TIMEOUT seconds, with its
# session storage wiped and an in-memory cache, because the tool keeps the
# resolved MPD in session storage and would otherwise hand document N the
# previous document's manifest.
#
# Docker on this host is rootless: root in the container is the invoking user
# on the host, so the reports come out owned by the caller with no chown.
#
# Segment-level modules are NOT run (no GPAC in this image, see UPSTREAM).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGE="${SGAI_DASHIF_IMAGE:-$(sed -n 's/^image=//p' "$HERE/UPSTREAM")}"
IN="$(cd "${1:?usage: run.sh <in-dir> <out-dir>}" && pwd)"
OUT="$(cd "${2:?usage: run.sh <in-dir> <out-dir>}" && pwd)"
DOC_TIMEOUT="${SGAI_DASHIF_DOC_TIMEOUT:-120}"

docker image inspect "$IMAGE" >/dev/null 2>&1 || {
  echo "no image $IMAGE — run bin/dashif/build.sh" >&2; exit 3; }

# Named, so that this run — and only this run — is removed if we are killed.
NAME="sgai-dashif-$$-$RANDOM"
trap 'docker rm -f "$NAME" >/dev/null 2>&1 || true' EXIT INT TERM

docker run --rm --name "$NAME" --network none \
  --memory "${SGAI_DASHIF_RUN_MEMORY:-2g}" --cpus "${SGAI_DASHIF_RUN_CPUS:-1}" \
  -e OTEL_SDK_DISABLED=true -e QUEUE_CONNECTION=sync -e CACHE_STORE=array \
  -e DOC_TIMEOUT="$DOC_TIMEOUT" \
  -v "$IN:/in:ro" -v "$OUT:/out" "$IMAGE" bash -c '
    for f in /in/*.mpd; do
      [ -e "$f" ] || continue
      n="$(basename "$f" .mpd)"
      rm -rf /app/storage/sessions/*
      timeout "$DOC_TIMEOUT" php artisan app:analyze-manifest "$f" "Global Module" "IOP MPD" \
        > "/out/$n.json" 2> "/out/$n.err" \
        || { rc=$?; [ $rc = 124 ] && echo "exit 124: timed out after ${DOC_TIMEOUT}s" >> "/out/$n.err" || echo "exit $rc" >> "/out/$n.err"; }
    done'
