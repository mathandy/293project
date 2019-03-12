"""

Usage
-----
* Example with L1 ~ (64, 8, 64) and L2 ~ (4096, 8, 64)::

    $ python cache.py rot 250 32 8 64 32768 8 64 2097152


* See "test_cache.sh" for a bash script example example.

"""
from __future__ import division, print_function
from random import uniform
from math import floor, ceil, sin, cos, radians
from cachesim import CacheSimulator, Cache, MainMemory
import numpy as np
from pprint import pprint


def pixel_address(x, y, w, offset=0, pixel_size=3):
    idx = x + y*w
    return idx * pixel_size + offset


def reflect_101(x, dimension_length):
    if x < 0:
        return abs(x)
    if x >= dimension_length:
        return dimension_length - 2 - (x % dimension_length)
    return x


def simulate_reads(transform_generator, image_dimensions, n_images, cache,
                   address_lookup=pixel_address, border_fcn=reflect_101):
    w, h = image_dimensions

    record = []
    for k in range(n_images):
        offset = w*h*k*3
        interp_nec, transform = transform_generator(image_dimensions)
        for x_prime in range(w):
            for y_prime in range(h):
                x, y = transform(x_prime, y_prime)
                if interp_nec:
                    x1, x2 = floor(x), ceil(x)
                    y1, y2 = floor(y), ceil(y)
                    x1, y1, x2, y2 = (border_fcn(x1, w), border_fcn(y1, h),
                                      border_fcn(x2, w), border_fcn(y2, h))

                    # is the order of these loads always optimal?
                    cache.load(address_lookup(x1, y1, w, offset), 3)
                    cache.load(address_lookup(x2, y1, w, offset), 3)
                    cache.load(address_lookup(x1, y2, w, offset), 3)
                    cache.load(address_lookup(x2, y2, w, offset), 3)
                    record += [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]
                else:
                    x, y = border_fcn(x, w), border_fcn(y, h)
                    cache.load(address_lookup(x, y, w, offset), 3)
                    record = [(x, y)]

    return cache, record


def create_cache(l1_ways, l1_block_size, l1_size, l2_ways, l2_block_size, l2_size):

    l2_sets = l2_size // (l2_block_size * l2_ways)
    l1_sets = l1_size // (l1_block_size * l1_ways)
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
    rotation = [[cos(theta), sin(theta)],
                [-sin(theta), cos(theta)]]
    interp_nec = True

    def transform(x, y):
        return np.dot(rotation, [[x], [y]]) + np.array([[w / 2], [h / 2]])

    return interp_nec, transform


def hflip_generator(image_dimensions):
    w, h = image_dimensions
    interp_nec = False

    def transform(x, y):
        return np.array([w - x - 1, y])

    return interp_nec, transform


def vflip_generator(image_dimensions):
    w, h = image_dimensions
    interp_nec = False

    def transform(x, y):
        return np.array([x, h - y - 1])

    return interp_nec, transform


generator_dict = {'rot': rotation_generator_101,
                  'vflip': vflip_generator,
                  'hflip': hflip_generator}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('kernel', help='which kernel (rot, hflip, or vflip).')
    parser.add_argument('image_size', type=int, help='Width of (square) images.')
    parser.add_argument('n_images', type=int, help='Number of images to process.')
    parser.add_argument('l1_ways', type=int)
    parser.add_argument('l1_block_size', type=int)
    parser.add_argument('l1_size', type=int)
    parser.add_argument('l2_ways', type=int)
    parser.add_argument('l2_block_size', type=int)
    parser.add_argument('l2_size', type=int)
    args = parser.parse_args()
    print("\nUser Parameters\n" + '-' * 15)
    pprint(vars(args))
    print()

    cs = create_cache(l1_ways=args.l1_ways,
                      l1_block_size=args.l1_block_size,
                      l1_size=args.l1_size,
                      l2_ways=args.l2_ways,
                      l2_block_size=args.l2_block_size,
                      l2_size=args.l2_size)

    cs, accesses = simulate_reads(transform_generator=generator_dict[args.kernel],
                                  image_dimensions=(args.image_size,) * 2,
                                  n_images=args.n_images,
                                  cache=cs,
                                  address_lookup=pixel_address,
                                  border_fcn=reflect_101)

    # report results
    cs.print_stats()
    # for l in cs.levels():
    #     st = l.stats()
    #     print(l.name, st['MISS_count'] / st['HIT_count'])
