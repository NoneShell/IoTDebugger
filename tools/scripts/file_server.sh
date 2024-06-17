#!/bin/sh

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <ROOT_DIR> <PORT>"
    exit 1
fi

BUSYBOX_PATH="${BUSYBOX_PATH}"
if [ ! -x "$BUSYBOX_PATH" ]; then
    echo "Please set BUSYBOX_PATH to the busybox binary"
    exit 1
fi

ROOT_DIR=$1
PORT=$2

iptables -I INPUT -p tcp --dport $PORT -j ACCEPT

$BUSYBOX_PATH tcpsvd -vE 0.0.0.0 $PORT $BUSYBOX_PATH ftpd -w $ROOT_DIR

echo "Server started on port $PORT"
