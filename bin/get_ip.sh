#!/bin/sh

os=$(uname)

if [ ${os} == "Darwin" ]; then
    for ip in $(ifconfig | grep inet | grep -v inet6 | awk '{print $2}');
    do
        echo ${ip}
    done
fi
