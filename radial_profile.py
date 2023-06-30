# felix zimmermann, github.com/fzimmermann89

import numpy as np

def radial_profile(data, center=None, calcStd=False, os=1):
    """
    calculates a ND radial profile of data around center. will ignore nans
    calStd: calculate standard deviation, return tuple of (profile, std)
    os: oversample by a factor. With default 1 the stepsize will be 1 pixel, with 2 it will be .5 pixels etc.
    """
    if center is None:
        center = np.array(data.shape) // 2
    if len(center) != data.ndim:
        raise TypeError("center should be of length data.ndim")
    center = np.array(center)[tuple([slice(len(center))] + data.ndim * [None])]
    ind = np.indices(data.shape)
    r = (np.rint(os * np.sqrt(((ind - center) ** 2).sum(axis=0)))).astype(int)
    databin = np.bincount(r.ravel(), (np.nan_to_num(data)).ravel())
    nr = np.bincount(r.ravel(), ((~np.isnan(data)).astype(float)).ravel())
    radialprofile = databin / nr
    if not calcStd:
        return radialprofile

    data2bin = np.bincount(r.ravel(), (np.nan_to_num(data ** 2)).ravel())
    radial2profile = data2bin / nr
    std = np.sqrt(radial2profile - radialprofile ** 2)
    return radialprofile, std
