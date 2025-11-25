#!/bin/bash
# Backup Script for El Jefe Dashboard

set -e

BACKUP_DIR="./backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="eljefe_backup_$DATE"

mkdir -p $BACKUP_DIR

echo "📦 Starting backup: $BACKUP_NAME"

# Create backup archive
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" \
    uploads/ \
    logs/ \
    config/ \
    --exclude="logs/*.log" \
    --exclude="logs/*.log.*"

echo "✅ Backup completed: $BACKUP_DIR/$BACKUP_NAME.tar.gz"

# Cleanup old backups (keep last 30 days)
find $BACKUP_DIR -name "eljefe_backup_*.tar.gz" -mtime +30 -delete

echo "🧹 Old backups cleaned up"
