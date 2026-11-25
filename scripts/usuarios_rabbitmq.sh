#!/usr/bin/env bash
set -euo pipefail
source .env
R="docker compose exec -T rabbitmq rabbitmqctl"

crear() {
    $R add_user "$1" "$2" 2>/dev/null || $R change_password "$1" "$2"
    $R set_permissions -p / "$1" "$3" "$4" "$5"
}

crear ventas "$RMQ_CLAVE_VENTAS" \
    '^tienda\.eventos$' '^tienda\.eventos$' '^$'

crear ia "$RMQ_CLAVE_IA" \
    '^inferencias$' '^amq\.default$' '^$'

crear worker "$RMQ_CLAVE_WORKER" \
    '^inferencias$' '^$' '^inferencias$'

crear notificaciones "$RMQ_CLAVE_NOTIF" \
    '^(tienda\.eventos|notificaciones)$' \
    '^notificaciones$' \
    '^(tienda\.eventos|notificaciones)$'

$R list_permissions -p /