#!/bin/sh

mode=$1
program=$2
port=$3

gdbserver_cmd() {
    if [ ! -x "${BIN_PATH}/gdbserver" ]; then
        echo "[!] gdbserver not found in ${BIN_PATH}"
        exit 1
    fi
    "${BIN_PATH}/gdbserver" "$@"
}

pidof_cmd() {
    if [ ! -x "${BIN_PATH}/pidof" ]; then
        echo "[!] pidof not found in ${BIN_PATH}"
        exit 1
    fi
    "${BIN_PATH}/busybox" pidof "$1"
}

if [ "$#" -lt 2 ]; then
    echo "Usage: $0 <-m | -s> <PROGRAM | PID> [PORT]"
    echo " -m : multi mode, program will be attached more than once"
    echo " -s : single mode, program will be attached once"
    exit 1
fi

if [ -z "$port" ]; then
    echo "[+] No port provided: defaulting to 6666"
    port="6666"
fi

if [ -z "$program" ]; then
    echo "[!] Please specify program name or PID"
    exit 1
fi

if [ "$mode" != "-m" ] && [ "$mode" != "-s" ]; then
    echo "[!] Invalid mode, please use -m or -s"
    exit 1
fi

case "$program" in
    ''|*[!0-9]*)
        echo "[*] Program mode"
        pid=$(pidof_cmd $program)
        if [ -z "$pid" ]; then
            echo "[!] Process $program not found"
            exit 1
        fi
        ;;
    *)
        echo "[*] PID mode"
        pid=$program
        ;;
esac

if [ "$mode" == "-m" ]; then
    while true; do
        if [ "$pid" = "$program" ]; then
            gdbserver_cmd :$port --attach $pid
        else
            gdbserver_cmd :$port $program
        fi
        gdbserver_cmd :$port --attach $pid
        sleep 1
    done
elif [ "$mode" == "-s" ]; then
    if [ "$pid" = "$program" ]; then
        gdbserver_cmd :$port --attach $pid
    else
        gdbserver_cmd :$port $program
    fi
fi

exit 0