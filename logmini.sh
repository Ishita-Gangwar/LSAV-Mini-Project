

#!/bin/bash

# --- Configuration ---
# The directory containing the logs you want to manage
LOG_DIR="$HOME/practice/test_logs"
# Max size in Kilobytes (1024 KB = 1 MB)
MAX_SIZE=1024
# How many days to keep compressed logs
RETENTION_DAYS=7

# Ensure the directory exists
if [ ! -d "$LOG_DIR" ]; then
    echo "Error: Directory $LOG_DIR does not exist."
    exit 1
fi

echo "Starting Log Rotation: $(date)"

# --- Step 1: Rotate and Compress ---
for file in "$LOG_DIR"/*.log; do
    # Check if files exist to avoid error if directory is empty
    [ -e "$file" ] || continue

    # Get file size in KB
    FILE_SIZE=$(du -k "$file" | cut -f1)
    # Get file age in days
FILE_AGE=$(find "$file" -mtime +$RETENTION_DAYS)

# Compress if file is BIGGER than MAX_SIZE OR OLDER than RETENTION_DAYS
if [ "$FILE_SIZE" -ge "$MAX_SIZE" ] || [ -n "$FILE_AGE" ]; then
    TIMESTAMP=$(date +%Y%m%d-%H%M%S)
    echo "Processing $file (Size: $FILE_SIZE KB / Age: Old)"
    
    mv "$file" "$file.$TIMESTAMP"
    gzip "$file.$TIMESTAMP"
    touch "$file"
    chmod 644 "$file"
else
    echo "Skipping $file (Small and Recent)"
fi
done

# --- Step 2: Cleanup Old Logs ---
echo "Cleaning up archives older than $RETENTION_DAYS days..."
find "$LOG_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -exec rm -v {} \;

echo "Log rotation complete."
