from cachesim import CacheSimulator, Cache, MainMemory
from math import floor, ceil, sin, cos, pi, radians
import numpy as np


def pixel_address(x, y, w, offset=0, pixel_size=3):
    idx = x + y*w
    return idx * pixel_size + offset


def simulate_reads(image_dimensions, transform, cache,
                   address_lookup=pixel_address):
    total_used = 0
    record = []
    for x_prime in range(image_dimensions[0]):
        for y_prime in range(image_dimensions[1]):
            x, y = transform(x_prime, y_prime)
            x1, x2 = floor(x), ceil(x)
            y1, y2 = floor(y), ceil(y)
            # print(x_prime, y_prime)
            # print(x, y)
            # print(x1, x2, y1, y2)
            # print()
            # input()
            record += [(x1, y1), (x2, y1), (x1, y2), (x2, y2)]

            # is the order of these loads always optimal?
            cache.load(address_lookup(x1, y1, w), 3)
            cache.load(address_lookup(x2, y1, w), 3)
            cache.load(address_lookup(x1, y2, w), 3)
            cache.load(address_lookup(x2, y2, w), 3)
            total_used += 4*3

            # if len(set(record)) * 3 > 512:
            #     import ipdb; ipdb.set_trace()
    return cache, record


if __name__ == '__main__':
    l2 = Cache("L2", 4096, 8, 64, "LRU")
    l1 = Cache("L1", 64, 8, 64, "LRU", store_to=l2, load_from=l2)
    mem = MainMemory()
    mem.load_to(l2)
    mem.store_from(l2)
    cs = CacheSimulator(l1, mem)

    w, h = (500, 500)
    theta = radians(10)
    r = [[cos(theta), sin(theta)],
         [sin(theta), cos(theta)]]

    def transform(x, y):
        return np.dot(r, [[x], [y]]) + np.array([[w/2], [h/2]])

    cs, accesses = simulate_reads((w, h), transform, cs)

    # report results
    cs.print_stats()
    for l in cs.levels():
        st = l.stats()
        print(l.name, st['MISS_count'] / st['HIT_count'])
