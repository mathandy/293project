import seaborn as sns
from matplotlib import pyplot as plt
import pandas as pd
from math import log2


def plot(data_frame, filename, hue, x_column, y_column):
    # plt.rc('text', usetex=True)
    # plt.rc('font', family='serif')

    sns.set(style="whitegrid")
    g, ax = plt.subplots(figsize=(6.5, 6.5))
    sns.despine(g, left=True, bottom=True)
    sns.scatterplot(x=x_column, y=y_column,
                    hue=hue,
                    # size='l1_size',
                    # palette="ch:r=-.2,d=.3_r",
                    # sizes=(1, 8),
                    # linewidth=0,
                    data=data_frame, ax=ax)

    g.savefig(filename)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('data_path', help='Path to CSV file containing data.')
    parser.add_argument('output_filename', help='Filename for output plot.')
    parser.add_argument('hue', help='')
    args = parser.parse_args()

    # load csv data into pandas DataFrame
    k = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
         'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen', 'fourteen',
         'fifteen', 'sixteen']

    df = pd.read_csv(args.data_path, ',')
    associativity_dict = (['fully-associative', 'direct-mapped'] +
                          ['%s-way' % k for k in range(2, df.ways.max() + 1)])
    l1_size_dict = (['fully-associative', 'direct-mapped'] +
                    ['%s-way' % k for k in range(2, df.ways.max() + 1)])
    # df['rows'] = df.rows.astype('str')
    # df['ways'] = df.ways.astype('str')
    # df['l1_size'] = df.l1_size.astype('category')
    df['rows'] = [k[x] for x in df['rows']]
    df['ways'] = [associativity_dict[int(x)] for x in df['ways']]
    df['l1_size'] = [str(int(x/1024)) + 'KiB' for x in df['l1_size']]

    new_column_names = ['Energy per Pixel (nJ)', 'Time per Pixel (ns)',
                        'Number of Cores', 'Cache Associativity', 'L1 Size']
    name_change_dict = dict(zip(df.columns, new_column_names))
    df = df.rename(columns=name_change_dict)

    # create plot
    plot(data_frame=df,
         filename=args.output_filename,
         hue=name_change_dict.get(args.hue, args.hue),
         x_column=new_column_names[0],
         y_column=new_column_names[1])
