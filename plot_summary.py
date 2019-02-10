#!/usr/bin/env python

import re
import os
import matplotlib.pyplot as plt
import numpy as np


def plot_summary(filename, xvals, out=None, xlabel='', ylabel='', title=''):
    yvals = []
    with open(filename) as summary:
        for line in summary:
            y_string = re.split(r'\s{2,}', line.strip())[0]
            y = int(y_string.replace(',', ''))
            yvals.append(y)
    yvals = np.array(yvals)

    # assert len(xvals) == len(yvals)
    if len(xvals) != len(yvals):
        import ipdb; ipdb.set_trace()

    plt.plot(xvals, yvals)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    # plt.grid(True)

    plt.tight_layout()
    if out is None:
        out = os.path.splitext(os.path.basename(filename))[0]
    plt.savefig(out)


if __name__ == '__main__':
    # parse command line arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('summary',
        help='Path to summary file.')
    parser.add_argument('x_min', type=int,
        help='Minimum x-value.')
    parser.add_argument('delta_x', type=int,
        help='distance between consecutive x-values.')
    parser.add_argument('x_max', type=int,
        help='Maximum x-value.')
    parser.add_argument('-o', '--plot_filename',
        help='Where to save output figure.')
    parser.add_argument('-x', '--xlabel', default='',
        help='Name for x-axis')
    parser.add_argument('-y', '--ylabel', default='',
        help='Name for y-axis')
    parser.add_argument('-t', '--title', default='',
        help='Title')
    args = parser.parse_args()

    x_values = np.arange(args.x_min, args.x_max + 1, args.delta_x)
    plot_summary(filename=args.summary,
                 xvals=x_values,
                 out=args.plot_filename,
                 xlabel=args.xlabel,
                 ylabel=args.ylabel,
                 title=args.title)
