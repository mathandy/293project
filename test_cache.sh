# Example
# l2_info = (4096, 8, 64)
# l1_info = (64, 8, 64)
n=32
w=250

l1sz=32768
l1ways=8
l1bs=64

l2sz=2097152
l2ways=8
l2bs=64

for kernel in {rot,hflip,vflip}; do
	args="cache.py $kernel $w $n $l1ways $l1bs $l1sz $l2ways $l2bs $l2sz"
	echo "$args"
    python "$args"
done
