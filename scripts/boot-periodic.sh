#!/bin/bash

if [ $# -ne 6 ]; then
    echo "Usage: "$0" <nova base name> <image name> <lease ID> <total nodes> <nodes per boot> <sleep period>"
    exit 1
fi

name=$1
image=$2
lease=$3
nodes=$4
npb=$5
period=$6

if (( $nodes % $npb != 0 )); then
    echo "<total nodes> must be an even multiple if <nodes per boot>"
    exit 1
fi

LOG="$(date +%h-%m-%y-%H:%M).log"
echo > $LOG
echo "Saving boot info to $LOG"

iterations=$(($nodes/$npb))

for iter in $(seq 0 $(($iterations-1))); do
    base=$(($iter*$npb))

    for node in $(seq 1 $npb); do
        node_name="$name-$(($base+$node))"
        nova boot --flavor baremetal \
            --image $image \
            --key-name pet-lab-2 \
            --nic net-name=sharednet1 \
            --hint reservation=$lease \
            $node_name &>> $LOG
    done

    for i in $(seq 1 $period); do
        sleep 1
        echo "Sleeping for $(($period - $i)) seconds ..."
    done
done
