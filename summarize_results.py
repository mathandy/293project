#!/usr/bin/env python

import os
import pandas as pd


def summarize(results_dir, output_filename, top_k=3, prefix='',
              postfix='.csv', ignore=None, sort_by_energy=True):

    for fn in os.listdir(results_dir):

        if not fn[:len(prefix)] == prefix:
            continue
        if not fn.endswith(postfix):
            continue
        if ignore is not None and ignore in fn:
            continue

        fn_full = os.path.join(results_dir, fn)

        # write summary for this file
        df = pd.read_csv(fn_full, ',')
        if sort_by_energy:
            top_results = df.sort_values(by='energy per pixel (nJ)')[1:top_k+1]
        else:
            top_results = df.sort_values(by='time per pixel (ns)')[1:top_k+1]
        with open(output_filename, 'a+') as f:
            f.write(fn + '\n' + str(top_results) + '\n')


if __name__ == '__main__':
    # parse command line arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('results_dir', help='Path to results directory.')
    parser.add_argument('output_filename', help='Where to save summary.')
    parser.add_argument('-k', '--top_k', default=3, type=int,
                        help='Include the top k results for each file.')
    parser.add_argument('--prefix', default='',
                        help='Only include files with this prefix.')
    parser.add_argument('--postfix', default='.csv',
                        help='Only include files with this postfix.')
    parser.add_argument('--ignore', default=None,
                        help='Do not include files with this in name.')
    parser.add_argument('--energy', default=False, action='store_true',
                        help='Sort by energy.')
    args = parser.parse_args()

    # create requested summary
    summarize(results_dir=args.results_dir,
              output_filename=args.output_filename,
              top_k=args.top_k,
              prefix=args.prefix,
              postfix=args.postfix,
              sort_by_energy=args.energy)
