#!/bin/bash

# Parameters
declare -a MODES=("no_interpolation_necessary" "interpolation_necessary" "affine" "rot" "rot90" "flip" "hflip" "vflip" "scale" "ssr" "none")
DEFAULT_IMAGE_SIZE=250
DEFAULT_BATCH_SIZE=100
STAT_FLAGS="-B -e task-clock,context-switches,cpu-migrations,page-faults,LLC-loads,LLC-load-misses,LLC-stores,LLC-store-misses,LLC-prefetch-misses,cache-references,cache-misses,cycles,instructions,branches,branch-misses"
declare -a METRICS=("LLC-load-misses" "branch-misses")


mkdir results
mkdir plots

# get results for various image sizes
outdir=results/image_size
xmin=50
deltax=50
xmax=2000
# mkdir $outdir
# for s in $(seq $xmin $deltax $xmax); do
# 	for mode in "${MODES[@]}"; do
# 		out=$outdir/stat_${mode}_${s}_${DEFAULT_BATCH_SIZE}.txt
# 		echo $out
# 		perf stat -o $out ${STAT_FLAGS} python benchmark.py test_images $mode --resize $s -n ${DEFAULT_BATCH_SIZE} -p --no_profile

# 		# grab any desired metrics and append them to a summary file
# 		for metric in "${METRICS[@]}"; do
# 			summary=$outdir/summary_${mode}_$metric.txt
# 			cat $out | grep $metric >> $summary
			
# 		done
# 	done
# done 

# plot summaries
for mode in "${MODES[@]}"; do
	for metric in "${METRICS[@]}"; do
		summary=$outdir/summary_${mode}_$metric
		python plot_summary.py $summary.txt $xmin $deltax $xmax --plot_filename $summary --xlabel "Image Size (px^2)" --ylabel $metric --title "Image Size vs. $metric"
	done
done

# get results for various batch sizes
outdir=results/batch_size
xmin=1
deltax=1
xmax=500
# mkdir $outdir
# for n in $(seq $xmin $deltax $xmax); do
# 	for mode in "${MODES[@]}"; do
# 		out=$outdir/stat_${mode}_${DEFAULT_IMAGE_SIZE}_$n.txt
# 		echo $out
# 		perf stat -o $out ${STAT_FLAGS} python benchmark.py test_images $mode --resize ${DEFAULT_IMAGE_SIZE} -n $n -p  --no_profile

# 		# grab any desired metrics and append them to a summary file
# 		for metric in "${METRICS[@]}"; do
# 			cat $out | grep $metric >> $outdir/summary_${mode}_$metric.txt
# 		done
# 	done
# done

# plot summaries
for mode in "${MODES[@]}"; do
	for metric in "${METRICS[@]}"; do
		summary=$outdir/summary_${mode}_$metric
		python plot_summary.py $summary.txt $xmin $deltax $xmax --plot_filename $summary --xlabel "Batch Size" --ylabel $metric --title "Batch Size vs. $metric"
	done
done
