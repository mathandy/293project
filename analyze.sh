#!/bin/bash

# Parameters
declare -a MODES=("no_interpolation_necessary" "interpolation_necessary" "affine" "rot" "rot90" "flip" "hflip" "vflip" "scale" "ssr" "none")
DEFAULT_IMAGE_SIZE=250
DEFAULT_BATCH_SIZE=100
STAT_FLAGS="-B -e task-clock,context-switches,cpu-migrations,page-faults,LLC-loads,LLC-load-misses,LLC-stores,LLC-store-misses,LLC-prefetch-misses,cache-references,cache-misses,cycles,instructions,branches,branch-misses"
declare -a METRICS=("LLC-load-misses" "branch-misses")


mkdir results

# get results for various image sizes
outdir=results/image_size
mkdir $outdir
for s in $(seq 50 50 2000); do
	for mode in "${MODES[@]}"; do
		out=$outdir/stat_${mode}_${s}_${DEFAULT_BATCH_SIZE}.txt
		echo $out
		perf stat -o $out ${STAT_FLAGS} python benchmark.py test_images $mode --resize $s -n ${DEFAULT_BATCH_SIZE} -p --no_profile

		# grab any desired metrics and append them to a summary file
		for metric in "${METRICS[@]}"; do
			cat $out | grep $metric >> $outdir/summary_${mode}_$metric.txt
		done
	done
done 

# get results for various batch sizes
outdir=results/batch_size
mkdir $outdir
for n in {1..500}; do
	for mode in "${MODES[@]}"; do
		out=$outdir/stat_${mode}_${DEFAULT_IMAGE_SIZE}_$n.txt
		echo $out
		perf stat -o $out ${STAT_FLAGS} python benchmark.py test_images $mode --resize ${DEFAULT_IMAGE_SIZE} -n $n -p  --no_profile

		# grab any desired metrics and append them to a summary file
		for metric in "${METRICS[@]}"; do
			cat $out | grep $metric >> $outdir/summary_${mode}_$metric.txt
		done
	done
done
