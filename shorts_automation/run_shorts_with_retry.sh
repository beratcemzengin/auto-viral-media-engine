#!/bin/bash
# run_shorts_with_retry.sh
# Automated retry loop wrapper for YouTube Shorts pipeline.
# Retries up to 3 times (waiting 10m then 20m) if rendering or publishing fails.

# Determine repo directory
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd "$SCRIPTPATH"

export ALLOW_YOUTUBE_UPLOAD=1

TIMESTAMP=$(date +%Y%m%d_%H%M)
LOG_FILE="logs/shorts_${TIMESTAMP}.log"
mkdir -p logs

run_pipeline() {
    local attempt=$1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Attempt ${attempt}/3 starting ===" >> "$LOG_FILE"
    ./../venv/bin/python3 main.py >> "$LOG_FILE" 2>&1
    return $?
}

# Attempt 1
run_pipeline 1
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Attempt 1 failed (exit code: ${EXIT_CODE}). Retrying in 10 minutes..." >> "$LOG_FILE"
    sleep 600

    # Attempt 2
    run_pipeline 2
    EXIT_CODE=$?
fi

if [ $EXIT_CODE -ne 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Attempt 2 failed (exit code: ${EXIT_CODE}). Retrying in 20 minutes for the final time..." >> "$LOG_FILE"
    sleep 1200

    # Attempt 3 (final)
    run_pipeline 3
    EXIT_CODE=$?
fi

if [ $EXIT_CODE -eq 0 ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Success! Pipeline completed successfully." >> "$LOG_FILE"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ALL 3 ATTEMPTS FAILED. Diagnostic error email should have been sent." >> "$LOG_FILE"
fi

exit $EXIT_CODE
