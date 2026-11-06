#!/usr/bin/env bash
# Dumps the HiCognition MySQL database into MYSQL_BACKUP_DIR and deletes dumps older than
# BACKUP_KEEP_DAYS (default 14). If BACKUP_COPY_DIR is set, each dump is also copied there and
# old dumps are deleted there too. Settings come from the environment or, failing that, from the
# .env file in the repository root. Meant to run from cron on the docker host, for example:
#
#   PATH=/usr/local/bin:/usr/bin:/bin
#   30 2 * * * /path/to/hicognition/mysql/backup_db.sh >> /path/to/hicognition/logs/backup.log 2>&1
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"

# value of a variable in .env, empty if it is not set there
env_file_value() {
    [[ -f .env ]] || return 0
    sed -n "s/^$1=//p" .env | tail -n 1
}

backup_dir="${MYSQL_BACKUP_DIR:-$(env_file_value MYSQL_BACKUP_DIR)}"
backup_dir="${backup_dir:-./db_backups}"
copy_dir="${BACKUP_COPY_DIR:-$(env_file_value BACKUP_COPY_DIR)}"
keep_days="${BACKUP_KEEP_DAYS:-$(env_file_value BACKUP_KEEP_DAYS)}"
keep_days="${keep_days:-14}"

mkdir -p "$backup_dir"
dump="$backup_dir/hicognition_$(date +%Y-%m-%d_%H%M).sql.gz"

# --single-transaction gives a consistent dump without locking the InnoDB tables;
# MYSQL_PWD keeps the password out of the process list
docker exec mysql sh -c 'export MYSQL_PWD="$MYSQL_PASSWORD"; exec mysqldump -h127.0.0.1 -uhicognition --single-transaction --no-tablespaces --routines --triggers hicognition' \
    | gzip > "$dump.partial"

# mysqldump ends a complete dump with this comment; anything else is a truncated dump
if ! gzip -dc "$dump.partial" | tail -n 1 | grep -q "^-- Dump completed"; then
    echo "$(date '+%F %T') ERROR: $dump.partial is incomplete, kept for inspection" >&2
    exit 1
fi
mv "$dump.partial" "$dump"
echo "$(date '+%F %T') wrote $dump ($(du -h "$dump" | cut -f1))"

if [[ -n "$copy_dir" ]]; then
    mkdir -p "$copy_dir"
    cp "$dump" "$copy_dir/"
    echo "$(date '+%F %T') copied to $copy_dir"
fi

for dir in "$backup_dir" ${copy_dir:+"$copy_dir"}; do
    find "$dir" -maxdepth 1 -name 'hicognition_*.sql.gz' -mtime +"$keep_days" -print -delete
done
