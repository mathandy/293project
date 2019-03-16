#!/usr/bin/env python
import os
try:
    from cache import main
except ImportError:
    from .cache import main

dram_multiplier = 2
store_to_cache = True

batch_sizes = [1, 2, 4, 8, 16, 32, 64]
sizes = [100, 250]

l1_sizes = [2**n for n in range(12, 16)]  # note 2**15 = 32768
degrees_of_associativity = [1]
rows_of_parallelism = [1, 4, 8]
results_dir = 'results/xnew-batch-size-test'
# os.mkdir(results_dir)

for size in sizes:
    for n_images in batch_sizes:
        for kernel in ['rot', 'hflip', 'vflip']:
            print('\n' + '='*25 + '\n' + kernel + '\n' + '='*25 + '\n')

            # create output filename
            out_basename = kernel + '_%sx%s' % (n_images, size) + '.csv'
            if store_to_cache:
                out_basename = 'store2cache_' + out_basename
            out_filename = os.path.join(results_dir, out_basename)

            results = 'time per pixel (ns),energy per pixel (nJ),rows,ways,l1_size\n'
            for rows in rows_of_parallelism:
                for l1_size in l1_sizes:
                    break_now = False
                    for ways in degrees_of_associativity:

                        config = "rows=%s, ways=%s; l1_size=%s" % (rows, ways, l1_size)
                        print(config)
                        try:
                            time_pp, energy_pp = main(kernel=kernel,
                                                      image_size=size,
                                                      n_images=n_images,
                                                      l1_ways=ways,
                                                      l2_ways=ways,
                                                      l1_block_size=64,
                                                      l2_block_size=64,
                                                      l1_size=l1_size,
                                                      l2_size=2097152,
                                                      parallelism=rows,
                                                      store_to_cache=store_to_cache,
                                                      dram_multiplier=dram_multiplier,
                                                      verbose=False)
                        except Exception as e:
                            time_pp, energy_pp = 'error', 'error'
                            print("Exception encountered w/ config=%s\nException:\n%s"
                                  "" % (config, e))
                            break_now = True
                        if break_now:
                            break

                        results += ('%s,%s,%s,%s,%s\n'
                                    '' % (time_pp, energy_pp, rows, ways, l1_size))

            with open(out_filename, 'w+') as f:
                f.write(results)
