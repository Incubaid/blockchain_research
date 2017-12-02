
# defs

## ring

- 256 servers in a ring
- the first byte of a hash defines where the master is running
- each server runs tarantool server & is the master
- each server+1 is the part 2 of the master cluster (so is like double ring)


