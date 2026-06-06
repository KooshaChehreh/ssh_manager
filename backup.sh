#!/usr/bin/env bash

set -euo pipefail

# مسیر دایرکتوری همین اسکریپت
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.env"

# لود کردن متغیرها از .env کنار اسکریپت
if [[ -f "${ENV_FILE}" ]]; then
    set -a
    source "${ENV_FILE}"
    set +a
else
    echo "فایل .env پیدا نشد: ${ENV_FILE}" >&2
    exit 1
fi

export AWS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY
export AWS_ENDPOINT_URL="https://s3.ir-thr-at1.arvanstorage.ir"

S3_BUCKET="ssh-manager"
S3_PREFIX="postgres-backups"

DB_CONTAINER="db"
DB_NAME="${DB_NAME:-postgres}"
DB_USER="${DB_USER:-postgres}"

RETENTION_DAYS=7

TMP_DIR="/tmp/db_backups"
LOG_FILE="/var/log/db_backup.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "${LOG_FILE}"
}

trap 'log "خطا در خط $LINENO. بکاپ ناتمام ماند."' ERR

mkdir -p "${TMP_DIR}"

TIMESTAMP="$(date '+%Y%m%d_%H%M%S')"
FILENAME="panel_${DB_NAME}_${TIMESTAMP}.sql.gz"
TMP_FILE="${TMP_DIR}/${FILENAME}"

log "شروع بکاپ‌گیری از دیتابیس '${DB_NAME}'..."

docker compose exec -T "${DB_CONTAINER}" \
    pg_dump -U "${DB_USER}" -d "${DB_NAME}" \
    | gzip > "${TMP_FILE}"

if [[ ! -s "${TMP_FILE}" ]]; then
    log "فایل بکاپ خالیه. عملیات متوقف شد."
    rm -f "${TMP_FILE}"
    exit 1
fi

BACKUP_SIZE="$(du -h "${TMP_FILE}" | cut -f1)"
log "دامپ ساخته شد: ${FILENAME} (${BACKUP_SIZE})"

log "در حال آپلود روی آروان..."
aws s3 cp "${TMP_FILE}" "s3://${S3_BUCKET}/${S3_PREFIX}/${FILENAME}" \
    --endpoint-url "${AWS_ENDPOINT_URL}"

log "آپلود با موفقیت انجام شد: s3://${S3_BUCKET}/${S3_PREFIX}/${FILENAME}"

rm -f "${TMP_FILE}"

log "بررسی بکاپ‌های قدیمی‌تر از ${RETENTION_DAYS} روز..."

CUTOFF_DATE="$(date -d "-${RETENTION_DAYS} days" '+%Y-%m-%d')"

aws s3 ls "s3://${S3_BUCKET}/${S3_PREFIX}/" \
    --endpoint-url "${AWS_ENDPOINT_URL}" \
| while read -r line; do
    FILE_DATE="$(echo "${line}" | awk '{print $1}')"
    FILE_NAME="$(echo "${line}" | awk '{print $4}')"

    [[ -z "${FILE_NAME}" ]] && continue

    if [[ "${FILE_DATE}" < "${CUTOFF_DATE}" ]]; then
        log "حذف بکاپ قدیمی: ${FILE_NAME}"
        aws s3 rm "s3://${S3_BUCKET}/${S3_PREFIX}/${FILE_NAME}" \
            --endpoint-url "${AWS_ENDPOINT_URL}"
    fi
done

log "Database backup successfully done."
