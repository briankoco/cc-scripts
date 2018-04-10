#!/bin/sh

declare -a lease_0=(60)
declare -a lease_1=(103 109 110 116 118 123 124 125 126 127 130 133 136 138 139 144 147 76 84 90 94 97)

lease_0_id="3d8ef382-bc1b-415e-b3d1-a2ef19b3de9d"
lease_1_id="2a90e16f-7bb2-4b54-b65d-5c7ec5849fbe"

for node in ${lease_0[@]}; do
    full_node="passthrough-$node"
    nova delete $full_node
done

for node in ${lease_1[@]}; do
    full_node="passthrough-$node"
    nova delete $full_node
done

for node in ${lease_0[@]}; do
    full_node="passthrough-$node"
    nova boot --flavor baremetal --image kvm-and-docker-with-pci-passthrough-3.12.18 \
        --key-name pet-lab-2 --nic net-name=sharednet1 \
        --hint reservation=$lease_0_id $full_node 
done

for node in ${lease_1[@]}; do
    full_node="passthrough-$node"
    nova boot --flavor baremetal --image kvm-and-docker-with-pci-passthrough-3.12.18 \
        --key-name pet-lab-2 --nic net-name=sharednet1 \
        --hint reservation=$lease_1_id $full_node 
done
