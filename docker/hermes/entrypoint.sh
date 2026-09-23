#!/bin/sh
set -e
# Precisa ser PID 1 no final: o entrypoint oficial usa s6-overlay e sobe
# o dashboard. `sh -c '… && exec hermes gateway run'` pulava isso.
python3 /opt/ensure-holographic.py
exec /opt/hermes/docker/entrypoint-dispatch.sh gateway run
