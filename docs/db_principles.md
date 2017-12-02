
#planning

## phase 1

- 1 Tarantool master with 2+ slaves (can have quite some)
- if master is down, a new master is brought life (by people, promotion of slave)
- at least 2 slaves in archive datacenter on secure location

## phase 2: 100 nodes (only 1 ring)

- 256 Tarantool masters where each node+1 & node+2  & node+3 is the slave of the original 1 (so total containers = 256 * 4)
- the hash of md5 of id defines who is master
- they are all connected over ZeroTier
- automation in Kubernetes cluster of 300 VM's (100 nodes needed, each hosting 3 VM)
    - node 1 = vm 1, vm 101, vm 201
- people still involved to run this cluster

-  is master or slave fails, the restart VM somewhere & let the syncing work
-  in multiple TLog's we feed all changes, can be used by clients to rebuild the full namespaces without having to go to all the tarantool nodes


## phase 3: 1000 nodes

- no more people involved, to be further defined placement & recovery modes
- multiple rings are being build

# principles

## ID

- ANNNBBBB : A=byte 1 of blake 256 hash, NNN = namespace, BBBB = int autoincrement in the cluster
- there are 16 million namespaces

## 256 part rings

- for scale & security we distribute all items over 256 tarantools
- the first char of the blake 256 hash of the payload (data on the "Base" obj) defines which part of ring is responsible
- the previous is defined but id-1 and is valid in the tarantool server (no need to go to external tarantool)

## previous

- how to know last id, for each namespace 

## ip addresses of rings

- ip addr is on zerotier & logically arranged so direct mapping between ip addr & logical nr 10.A.B1.B2 
    -  A=X+0 for master, A=X+1 for slave1, A=X+2 for slave2, A=X+3 for slave3
    -  X is a nr between 1 & 250 (this is id of ring, so we can create 250 rings)
    -  B1-B2 is 256*256 address space for the Byte 1 starting at 1: 
        -  e.g. 00... -> uint16 1 -> 00.01
        -  e.g. 01... -> uint16 2 -> 00.02
        -  e.g. F0... -> uint16 241 (16*15+1)  -> 00.F1
    -  In other words if hash is 01aabbccddeeff... in ring 5 then following ip are -> 10.5.0.1,10.6.0.1,10.7.0.1,10.8.0.1