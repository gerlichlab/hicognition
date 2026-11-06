#!/usr/bin/env bash
# Dumps the HiCognition MySQL database into MYSQL_BACKUP_DIR and deletes dumps older than
# BACKUP_KEEP_DAYS days (default 14). If BACKUP_COPY_DIR is set, each dump is also copied there and
# old dumps are deleted there too; that folder must already exist, so that a share that is not
# mounted fails the run instead of filling the local disk. Settings come from the environment or,
# failing that, from the .env file in the repository root. Meant to run from cron on the docker
# host, for example:
#
#   PATH=/usr/local/bin:/usr/bin:/bin
#   30 2 * * * /path/to/hicognition/mysql/backup_db.sh >> /path/to/hicognition/logs/backup.log 2>&1
set -euo pipefail

# the dumps contain the user table with e-mail addresses and password hashes
umask 077

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

# deletes dumps, and the partial files of failed runs, older than keep_days days
delete_old_dumps() {
    find "$1" -maxdepth 1 \( -name 'hicognition_*.sql.gz' -o -name 'hicognition_*.sql.gz.partial' \) \
        -mmin +"$((keep_days * 24 * 60))" -print -delete
}

mkdir -p "$backup_dir"
dump_name="hicognition_$(date +%Y-%m-%d_%H%M).sql.gz"
dump="$backup_dir/$dump_name"

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
delete_old_dumps "$backup_dir"

[[ -n "$copy_dir" ]] || exit 0
if [[ ! -d "$copy_dir" ]]; then
    echo "$(date '+%F %T') ERROR: $copy_dir does not exist, $dump not copied" >&2
    exit 1
fi
cp "$dump" "$copy_dir/$dump_name.partial"
mv "$copy_dir/$dump_name.partial" "$copy_dir/$dump_name"
echo "$(date '+%F %T') copied to $copy_dir"
delete_old_dumps "$copy_dir"
