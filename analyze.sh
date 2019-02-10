#!/bin/bash

# Parameters
declare -a MODES=("no_interpolation_necessary" "interpolation_necessary" "affine" "rot" "rot90" "flip" "hflip" "vflip" "scale" "ssr" "none")
DEFAULT_IMAGE_SIZE=250
DEFAULT_BATCH_SIZE=100
STAT_FLAGS="-B -e task-clock,context-switches,cpu-migrations,page-faults,LLC-loads,LLC-load-misses,LLC-stores,LLC-store-misses,LLC-prefetch-misses,cache-references,cache-misses,cycles,instructions,branches,branch-misses"

mkdir results

# get results for various image sizes
outdir=results/image_size
mkdir $outdir
for s in $(seq 50 50 200); do
	echo "image_size: $s"
	for mode in "${MODES[@]}"; do
		echo "mode: $mode"
		out=$outdir/stat_$mode_$s_${DEFAULT_BATCH_SIZE}.txt
		perf stat -o $out ${STAT_FLAGS} python benchmark.py test_images $mode --resize $s -n ${DEFAULT_BATCH_SIZE} -p --no_profile
	done
done 

# get results for various batch sizes
outdir=results/batch_size
mkdir $outdir
for n in {1..10}; do
	echo "batch_size: $n"
	for mode in "${MODES[@]}"; do
		echo "mode: $mode"
		out=$outdir/stat_$mode_${DEFAULT_MAGE_SIZE}_$n.txt
		perf stat -o $out ${STAT_FLAGS} python benchmark.py test_images $mode --resize ${DEFAULT_IMAGE_SIZE} -n $n -p  --no_profile
	done
done
