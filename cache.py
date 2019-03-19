"""

Usage
-----
* Example with L1 ~ (64, 8, 64) and L2 ~ (4096, 8, 64)::

    $ python cache.py rot 250 32 8 8


* See "test_cache.sh" for a bash script example example.

"""

from __future__ import division, print_function
from random import uniform
from math import floor, ceil, sin, cos, radians
from cachesim import CacheSimulator, Cache, MainMemory
from pprint import pprint
import os
from shutil import copyfile

# defaults
DRAM_ACCESS_TIME = 52.7802
DRAM_READ_ENERGY = 25.25
DRAM_WRITE_ENERGY = 78.6838


def pixel_address(x, y, w, offset=0, pixel_size=3):
    idx = x + y*w
    return int(idx*pixel_size + offset)


def reflect_101(x, dimension_length):
    if x < 0:
        return abs(x)
    if x >= dimension_length:
        return dimension_length - 2 - (x % dimension_length)
    return x


def simulate_reads(transform_generator, image_dimensions, n_images, cache,
                   parallelism=1, address_lookup=pixel_address,
                   border_fcn=reflect_101, store_to_cache=False):
    w, h = image_dimensions

    record = []
    for k in range(n_images):
        write_offset = w*h*3*(k + n_images)
        read_offset = w*h*3*k
        interp_nec, transform = transform_generator(image_dimensions)
        for row_set in range(int(ceil(h/parallelism))):
            for x_prime in range(w):
                for row in range(parallelism):
                    y_prime = row_set * parallelism + row

                    x, y = transform(x_prime, y_prime)
                    if interp_nec:
                        x1, x2 = floor(x), ceil(x)
                        y1, y2 = floor(y), ceil(y)
                        x1, y1, x2, y2 = (border_fcn(x1, w), border_fcn(y1, h),
                                          border_fcn(x2, w), border_fcn(y2, h))

                        # is the order of these loads always optimal?
                        cache.load(address_lookup(x1, y1, w, read_offset), 3)
                        cache.load(address_lookup(x2, y1, w, read_offset), 3)
                        cache.load(address_lookup(x1, y2, w, read_offset), 3)
                        cache.load(address_lookup(x2, y2, w, read_offset), 3)
                        record += [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]
                    else:
                        x, y = border_fcn(x, w), border_fcn(y, h)
                        cache.load(address_lookup(x, y, w, write_offset), 3)
                        record = [(x, y)]
                    if store_to_cache:
                        cache.store(address_lookup(x, y, w, write_offset), 3)

    return cache, record


def create_cache(l1_ways, l1_block_size, l1_size, l2_ways, l2_block_size, l2_size):

    if l1_ways == 0:
        l1_sets = 1
        l1_ways = l1_size // l1_block_size
    else:
        l1_sets = l1_size // (l1_block_size * l1_ways)

    if l2_ways == 0:
        l2_sets = 1
        l2_ways = l2_size // l2_block_size
    else:
        l2_sets = l2_size // (l2_block_size * l2_ways)

    l2 = Cache("L2", l2_sets, l2_ways, l2_block_size, replacement_policy="LRU")
    l1 = Cache("L1", l1_sets, l1_ways, l1_block_size, replacement_policy="LRU",
               store_to=l2, load_from=l2)
    mem = MainMemory()
    mem.load_to(l2)
    mem.store_from(l2)
    return CacheSimulator(l1, mem)


def rotation_generator_101(image_dimensions):
    """Uses border mode = cv2.BORDER_REFLECT_101, gfedcb|abcdefgh|gfedcba"""
    w, h = image_dimensions
    theta = radians(uniform(-90, 90))
    r = [[cos(theta), sin(theta)],
         [-sin(theta), cos(theta)]]
    interp_nec = True

    # def transform(x, y):
    #     return np.dot(r, [[x], [y]]) + np.array([[w / 2], [h / 2]])
    def transform(x, y):
        return [r[0][0]*x + r[0][1]*y + w/2, r[1][0]*x + r[1][1]*y + h/2]

    return interp_nec, transform


def hflip_generator(image_dimensions):
    w, h = image_dimensions
    interp_nec = False

    def transform(x, y):
        return [w - x - 1, y]

    return interp_nec, transform


def vflip_generator(image_dimensions):
    w, h = image_dimensions
    interp_nec = False

    def transform(x, y):
        return [x, h - y - 1]

    return interp_nec, transform


def create_cacti_cfg(ways, block_size, size, cfg_template='cache_template.cfg',
                     filename='tmp_cache.cfg'):
    copyfile(cfg_template, filename)
    with open(cfg_template) as template:
        cfg = template.read()

    cfg = cfg.replace('##SIZE', '-size (bytes) %s' % size)
    cfg = cfg.replace('##BLOCK_SIZE', '-block size (bytes) %s' % block_size)
    cfg = cfg.replace('##WAYS', '-associativity %s' % ways)

    with open(filename, 'w+') as out:
        out.write(cfg)


def parse_cacti_output(cacti_output, endline='\n'):
    s0 = "Access time (ns):"
    s1 = "Total dynamic associative search energy per access (nJ):"
    s2 = "Total dynamic read energy per access (nJ):"
    s3 = "Total dynamic write energy per access (nJ):"
    access_time, search_energy, read_energy, write_energy = None, None, None, None
    for line in cacti_output.split(endline):
        if s0 in line:
            access_time = float(line.split(':')[1])
        elif s1 in line:
            search_energy = float(line.split(':')[1])
        elif s2 in line:
            read_energy = float(line.split(':')[1])
        elif s3 in line:
            write_energy = float(line.split(':')[1])
        if access_time and search_energy and read_energy:
            break

    # sanity check
    assert isinstance(access_time, float) and isinstance(read_energy, float)

    if write_energy is None:
        print("Warning: write energy is being considered 0 (+ search energy).")
        write_energy = 0.0
    if search_energy is None:
        print("Warning: search energy is being considered 0.")
        search_energy = 0.0

    read_energy_per_access = search_energy + read_energy
    write_energy_per_access = search_energy + write_energy
    return access_time, read_energy_per_access, write_energy_per_access


def get_cactus_results(ways, block_size, size):
    tmp_cfg = 'tmp_cache.cfg'
    create_cacti_cfg(ways, block_size, size, filename=tmp_cfg)
    cacti_output = os.popen('cd cacti; ./cacti -infile ../%s; cd ..' % tmp_cfg).read()
    return parse_cacti_output(cacti_output)


generator_dict = {'rot': rotation_generator_101,
                  'vflip': vflip_generator,
                  'hflip': hflip_generator}


def main(kernel, image_size, n_images, l1_ways, l2_ways, parallelism=1,
         l1_block_size=64, l2_block_size=64, l1_size=32768, l2_size=2097152,
         dram_access_time=DRAM_ACCESS_TIME, dram_read_energy_per_access=DRAM_READ_ENERGY,
         dram_write_energy_per_access=DRAM_WRITE_ENERGY, dram_multiplier=1,
         store_to_cache=False, verbose=True):

    dram_access_time = dram_access_time * dram_multiplier
    dram_read_energy_per_access = dram_read_energy_per_access * dram_multiplier
    dram_write_energy_per_access = dram_write_energy_per_access * dram_multiplier

    cs = create_cache(l1_ways=l1_ways,
                      l1_block_size=l1_block_size,
                      l1_size=l1_size,
                      l2_ways=l2_ways,
                      l2_block_size=l2_block_size,
                      l2_size=l2_size)

    cs, accesses = simulate_reads(transform_generator=generator_dict[kernel],
                                  image_dimensions=(image_size,) * 2,
                                  n_images=n_images,
                                  cache=cs,
                                  parallelism=parallelism,
                                  address_lookup=pixel_address,
                                  border_fcn=reflect_101,
                                  store_to_cache=store_to_cache)

    l1_access_time, l1_read_energy_per_access, l1_write_energy_per_access = \
        get_cactus_results(l1_ways, l1_block_size, l1_size)
    l2_access_time, l2_read_energy_per_access, l2_write_energy_per_access = \
        get_cactus_results(l2_ways, l2_block_size, l2_size)

    l1, l2, dram = list(cs.levels())[:3]
    l1, l2, dram = l1.stats(), l2.stats(), dram.stats()
    l1_loads, l1_stores = l1['LOAD_count'], l1['STORE_count']
    l2_loads, l2_stores = l2['LOAD_count'], l2['STORE_count']
    dram_loads, dram_stores = dram['LOAD_count'], dram['STORE_count']

    l1_energy = (l1_loads * l1_read_energy_per_access +
                 l1_stores * l1_write_energy_per_access)
    l1_time = (l1_loads + l1_stores) * l1_access_time
    l2_energy = (l2_loads * l2_read_energy_per_access +
                 l2_stores * l2_write_energy_per_access)
    l2_time = (l2_loads + l2_stores) * l2_access_time
    dram_energy = (dram_loads + dram_stores) * dram_access_time
    dram_time = (dram_loads * dram_read_energy_per_access +
                 dram_stores * dram_write_energy_per_access)

    total_energy = l1_energy + l2_energy + dram_energy
    total_time = l1_time + l2_time + dram_time

    n_pixels = n_images * image_size**2
    energy_per_pixel = total_energy / n_pixels
    time_per_pixel = total_time / n_pixels

    # report results
    if verbose:
        print()
        print('Time per Pixel (ns):', time_per_pixel)
        print('Energy per Pixel (nJ):', energy_per_pixel)
        # print('L1/L2 Time Ratio:', l1_time / l2_time)
        # print('L1/L2 Energy Ratio:', l1_energy / l2_energy)
        print('L1/L2/DRAM loads: %s / %s / %s' % (l1_loads, l2_loads, dram_loads))
        print('L1/L2/DRAM stores: %s / %s / %s' % (l1_stores, l2_stores, dram_stores))
        print('L1/L2/DRAM time: %s / %s / %s' % (l1_time, l2_time, dram_time))
        print('L1/L2/DRAM energy: %s / %s / %s' % (l1_energy, l2_energy, dram_energy))
        print('L1/L2/DRAM time per access: %s / %s / %s'
              '' % (l1_access_time, l2_access_time, dram_access_time))
        print('L1/L2/DRAM read energy per access: %s / %s / %s'
              '' % (l1_read_energy_per_access, l2_read_energy_per_access,
                    dram_read_energy_per_access))
        print('L1/L2/DRAM write energy per access: %s / %s / %s'
              '' % (l1_write_energy_per_access, l2_write_energy_per_access,
                    dram_write_energy_per_access))
        # cs.print_stats()
    return time_per_pixel, energy_per_pixel

    
if __name__ == '__main__':

    # parse command line arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('kernel', help='which kernel (rot, hflip, or vflip).')
    parser.add_argument('image_size', type=int, help='Width of (square) images.')
    parser.add_argument('n_images', type=int, help='Number of images to process.')
    parser.add_argument('l1_ways', type=int)
    parser.add_argument('l2_ways', type=int)
    parser.add_argument('--l1_block_size', type=int, default=64)
    parser.add_argument('--l2_block_size', type=int, default=64)
    parser.add_argument('--l1_size', type=int, default=32768)
    parser.add_argument('--l2_size', type=int, default=2097152)
    parser.add_argument('-p', '--parallelism', type=int, default=1,
                        help="Number of rows to process in parallel.")
    parser.add_argument('--store_to_cache', default=False, action='store_true',
                        help="Number of rows to process in parallel.")
    parser.add_argument('-m', '--dram_multiplier', default=1, type=float,
                        help="(Hacky) Multiply DRAM measurements by this factor.")
    args = vars(parser.parse_args())

    # report CLI arguments
    print("\nUser Parameters\n" + '-' * 15)
    pprint(args)
    print()
    multiplier = args.pop('dram_multiplier')

    # run simulation
    main(verbose=True,
         dram_access_time=multiplier*DRAM_ACCESS_TIME,
         dram_read_energy_per_access=multiplier*DRAM_READ_ENERGY,
         dram_write_energy_per_access=multiplier*DRAM_WRITE_ENERGY,
         **args)
