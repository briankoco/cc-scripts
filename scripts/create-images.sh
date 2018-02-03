#!/bin/bash

for i in $(seq 0 47); do
    rm -f varbench-$i.img
    qemu-img create -f qcow2 -o backing_file=/home/cc/vms/disks/varbench-baseimage.img varbench-$i.img
done
