import numpy as np

def bootstrap_sample_idx(num_samples, boot_strap_size=None):
    """ Return idx for bootstrap sampling
    Taken and modified from http://nbviewer.jupyter.org/gist/aflaxman/6871948
    Parameters
    ----------
    num_samples : int
      datasize
    boot_strap_size : int, optional
      length of resampled array, equal to len(X) if n==None
    Results
    -------
    returns X_resamples
    """
    if boot_strap_size == None:
        boot_strap_size = len(num_samples)

    resample_i = np.floor(np.random.rand(boot_strap_size)*num_samples).astype(int)
    return resample_i