#!/bin/sh

#nova boot --flavor baremetal --image kvm-and-docker-2.3.2018 --key-name pet-lab-2 
#    --nic net-name=sharednet1 
#    --hint reservation=baa4e397-c55f-47a3-853d-a8359d468769 
#    --min-count 15 --max-count 15 
#    mantevo-compute-15

# Wait 15 min
#sleep 900

#nova boot --flavor baremetal --image kvm-and-docker-2.3.2018 --key-name pet-lab-2 
#    --nic net-name=sharednet1 
#    --hint reservation=baa4e397-c55f-47a3-853d-a8359d468769 
#    --min-count 10 --max-count 10 
#    mantevo-compute-25

# Wait 10 min
#sleep 600

nova boot --flavor baremetal --image kvm-and-docker-2.3.2018 --key-name pet-lab-2 \
    --nic net-name=sharednet1 \
    --hint reservation=42e44553-dbf4-403b-b9ed-8c0a89472c56 \
    --min-count 15 --max-count 15 \
    mantevo-compute-40

# Wait 15 min
sleep 900

nova boot --flavor baremetal --image kvm-and-docker-2.3.2018 --key-name pet-lab-2 \
    --nic net-name=sharednet1 \
    --hint reservation=42e44553-dbf4-403b-b9ed-8c0a89472c56 \
    --min-count 10 --max-count 10 \
    mantevo-compute-50

# Wait 10 min
sleep 600

nova boot --flavor baremetal --image kvm-and-docker-2.3.2018 --key-name pet-lab-2 \
    --nic net-name=sharednet1 \
    --hint reservation=c68195e4-1074-461e-8c8b-e25704e36150 \
    --min-count 15 --max-count 15 \
    mantevo-compute-65

# Wait 15 min
sleep 900

nova boot --flavor baremetal --image kvm-and-docker-2.3.2018 --key-name pet-lab-2 \
    --nic net-name=sharednet1 \
    --hint reservation=c68195e4-1074-461e-8c8b-e25704e36150 \
    --min-count 10 --max-count 10 \
    mantevo-compute-75

# Wait 10 min
sleep 600

nova boot --flavor baremetal --image kvm-and-docker-2.3.2018 --key-name pet-lab-2 \
    --nic net-name=sharednet1 \
    --hint reservation=9b2d7939-f1d9-425f-9bd5-d8123a945b75 \
    --min-count 15 --max-count 15 \
    mantevo-compute-90

# Wait 15 min
sleep 900

nova boot --flavor baremetal --image kvm-and-docker-2.3.2018 --key-name pet-lab-2 \
    --nic net-name=sharednet1 \
    --hint reservation=9b2d7939-f1d9-425f-9bd5-d8123a945b75 \
    --min-count 10 --max-count 10 \
    mantevo-compute-100

# Wait 10 min
sleep 600

nova boot --flavor baremetal --image kvm-and-docker-2.3.2018 --key-name pet-lab-2 \
    --nic net-name=sharednet1 \
    --hint reservation=2d7dba7d-52bc-4b14-8a03-8c19ba825295 \
    --min-count 15 --max-count 15 \
    mantevo-ib-15

# Wait 15 min
sleep 900

nova boot --flavor baremetal --image kvm-and-docker-2.3.2018 --key-name pet-lab-2 \
    --nic net-name=sharednet1 \
    --hint reservation=2d7dba7d-52bc-4b14-8a03-8c19ba825295 \
    --min-count 10 --max-count 10 \
    mantevo-ib-25

# Wait 10 min
sleep 600

nova boot --flavor baremetal --image kvm-and-docker-2.3.2018 --key-name pet-lab-2 \
    --nic net-name=sharednet1 \
    --hint reservation=d22096eb-a06e-4766-8634-b1441bd02178 \
    --min-count 8 --max-count 8 \
    mantevo-ib-33

# Wait 8 min
sleep 480


nova boot --flavor baremetal --image kvm-and-docker-2.3.2018 --key-name pet-lab-2 \
    --nic net-name=sharednet1 \
    --hint reservation=f0d0cbc2-4857-4b46-bc78-161408edec7b \
    --min-count 1 --max-count 1 \
    mantevo-compute-headnode
