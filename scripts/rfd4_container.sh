#!/usr/bin/env bash
# Run python (or any command) inside the RFD4-Proteina cu128 container with $BIND_PATHS bound.
# Machine-specific locations are environment variables (see config.example.env); SLURM account/partition lines removed.
AP=${APPTAINER:-apptainer}
SIF=${RFD4_SIF:?set RFD4_SIF}
exec $AP exec ${NV:-} --cleanenv --bind "${BIND_PATHS:?set BIND_PATHS (comma-separated)}" \
  --bind "${RFD4_WEIGHTS_DIR}:/weights/rfd4-proteina:ro" \
  --env "PYTHONPATH=,HF_HUB_OFFLINE=1,CLUSTER=local,DEBUG=false" "$SIF" "$@"
