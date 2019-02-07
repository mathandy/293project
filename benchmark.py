#!/usr/bin/env python
"""Andy and Jennifer's albumentations benchmark script.

Usage
-----
* Run all augmentations on each image in a directory

    $ python benchmark.py path/to/image/directory all


* Run only augmentations not involving interpolation on 100 randomly
generated 200 x 200 color images::

    $ python benchmark.py none no_interpolation_necessary -g 200 -n 100 -c 3


* To see a comparison of each image before and after augmentation, use the
--show flag::

    $ python benchmark.py path/to/image/directory all --show


* For more options::

    $ python benchmark.py -h


Prerequisites
-------------
To install all necessary prerequisites::

    $ pip install numpy, opencv-python, albumentations


"""

import cv2 as cv  # pip install opencv-python
from albumentations import (HorizontalFlip, ShiftScaleRotate, RandomRotate90,
                            Flip, OneOf, Compose, Rotate, RandomScale)
import numpy as np
import os


def preload_images_from_directory(image_dir, n_images=None, shuffle=True,
                                  extensions=('jpg', 'jpeg', 'png')):
    """Returns list of images (as numpy arrays) from directory `image_dir`.

    Parameters
    ----------
    image_dir (string)
        Path to the directory of images.
    n_images (int)
        The maximum number of images to include in returned list/generator.
    shuffle (bool)
        If true, images will be shuffled.
    extensions (list of strings)
        Acceptable image extensions.

    Returns
    -------
    images (generator of numpy arrays)
    """
    image_filenames = [os.path.join(image_dir, fn) for fn in os.listdir(image_dir) 
                       if os.path.splitext(fn)[-1] in extensions]

    if shuffle:
        np.random.shuffle(image_filenames)

    if n_images is not None:
        image_filenames = image_filenames[:n_images]

    return [cv.imread(fn) for fn in image_filenames]


def iterate_images_from_directory(image_dir, n_images=None, shuffle=True,
                                  extensions=('jpg', 'jpeg', 'png')):
    """Returns generator of images in directory `image_dir`.

    Parameters
    ----------
    image_dir (string)
        Path to the directory of images.
    n_images (int)
        The maximum number of images to include in returned list.
    shuffle (bool)
        If true, images will be shuffled.
    extensions (list of strings)
        Acceptable image extensions.

    Returns
    -------
    images (list of numpy arrays)
    """

    image_filenames = [os.path.join(image_dir, fn) for fn in os.listdir(image_dir)
                       if os.path.splitext(fn)[-1][1:] in extensions]

    if shuffle:
        np.random.shuffle(image_filenames)

    if n_images is not None:
        image_filenames = image_filenames[:n_images]

    for fn in image_filenames:
        yield cv.imread(fn)


def get_augmentation_fcn(mode, interpolation_method=cv.INTER_LINEAR):
    augmentation_dict = {
        'all': Compose([RandomRotate90(p=1.), 
                        Flip(p=1.), 
                        Rotate(p=1., interpolation=interpolation_method), 
                        RandomScale(p=1., interpolation=interpolation_method), 
                        ShiftScaleRotate(p=1., interpolation=interpolation_method)]),
        'any': OneOf([RandomRotate90(p=1.), 
                      Flip(p=1.), 
                      Rotate(p=1., interpolation=interpolation_method), 
                      RandomScale(p=1., interpolation=interpolation_method), 
                      ShiftScaleRotate(p=1., interpolation=interpolation_method)]),
        'no_interpolation_necessary': OneOf([RandomRotate90(p=1.), 
                                             Flip(p=1.)]),
        'interpolation_necessary': OneOf([Rotate(p=1., interpolation=interpolation_method), 
                                          RandomScale(p=1., interpolation=interpolation_method), 
                                          ShiftScaleRotate(p=1., interpolation=interpolation_method)]),
        'affine': Compose([ShiftScaleRotate(p=1., interpolation=interpolation_method), 
                           HorizontalFlip(p=0.5)]),
        'rot': Rotate(p=1., interpolation=interpolation_method),
        'rot90': RandomRotate90(p=1.)
    }
    return augmentation_dict[mode]


def show_before_and_after(before_image, after_image):


    h_diff = after_image.shape[0] - before_image.shape[0]
    if h_diff > 0:  # augmented is taller
        padding = 255 * np.ones((abs(h_diff),) + before_image.shape[1:],
                                dtype='uint8')
        before_image = np.vstack((padding, before_image))
    elif h_diff < 0:  # original is taller
        padding = 255 * np.ones((abs(h_diff),) + after_image.shape[1:],
                                dtype='uint8')
        after_image = np.vstack((padding, after_image))
    divider = 255 * np.ones((before_image.shape[0], 20, image.ndim),
                            dtype='uint8').squeeze()
    print('press any key to continue')
    cv.imshow('b/a', np.hstack((before_image, divider, after_image)))
    cv.waitKey(0)


if __name__ == '__main__':
    # parse command line arguments
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('image_dir', 
        help='directory of images.  Ignored if `--generate` flag invoked.')
    parser.add_argument('mode', 
        help='Which set of augmentations to use.')
    parser.add_argument('-p', '--preload', default=False, action='store_true', 
        help='Preload all images to memory.')
    parser.add_argument('-c', '--channels', default=3, type=int, 
        help='Number of channels to use when generating images (defaults '
             'to 3).  Ignored unless `--generate` flag is used.')
    parser.add_argument('-g', '--generate_images_of_size', default=None, type=int, 
        help='Use generated random images of this width and height.')
    parser.add_argument('-n', '--num_images', default=None, type=int, 
        help='Use this many images.')
    parser.add_argument('-i', '--interpolation_method', default=None, 
        help='Interpolation mode (not yet implemented, edit manually).')
    parser.add_argument('--show', default=False, action='store_true',
        help='Show each image before and after augmentation.')
    args = parser.parse_args()

    # create generator (or preload) images
    if args.generate_images_of_size is None:  # load images from directory
        if args.preload:
            images = preload_images_from_directory(image_dir=args.image_dir,
                                                   n_images=args.num_images,
                                                   shuffle=True,
                                                   extensions=('jpg', 'jpeg', 'png'))
        else:
            images = iterate_images_from_directory(image_dir=args.image_dir,
                                                   n_images=args.num_images,
                                                   shuffle=True,
                                                   extensions=('jpg', 'jpeg', 'png'))
    else:  # generate random images
        if args.num_images is None:
            raise ValueError('`--num_images` must be specified when using '
                             'randomly generated images.')
        shape = (args.num_images, args.generate_images_of_size, 
                 args.generate_images_of_size, args.channels)
        
        # in case grayscale is requested
        if args.channels == 1:
            shape = shape[:-1]

        if args.preload:
            images = (np.random.randint(0, 256, shape[1:], dtype='uint8'))
        else:
            images = np.random.randint(0, 256, shape, dtype='uint8')

    augment = get_augmentation_fcn(args.mode, interpolation_method=cv.INTER_LINEAR)
    for image in images:
        augmented_image = augment(**{'image': image})['image']

        if args.show:
            show_before_and_after(image, augmented_image)
