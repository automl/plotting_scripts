import numpy as np


def bootstrap_sample_idx(num_samples, boot_strap_size=None, rng=None):
    """ Return idx for bootstrap sampling
    Taken and modified from http://nbviewer.jupyter.org/gist/aflaxman/6871948
    Parameters
    ----------
    num_samples : int
      datasize
    boot_strap_size : int, optional
      length of resampled array, equal to len(X) if n==None
    rng : None|int|RandomState
      to make method deterministic
    Results
    -------
    returns X_resamples
    """

    if rng is not None:
        if type(rng) == np.int:
            np.random.seed(rng)
        elif type(rng) == tuple:
            np.random.set_state(rng)
        else:
            raise ValueError("Can't initialize seed with %s" % str(rng))

    if boot_strap_size == None:
        boot_strap_size = len(num_samples)

    resample_i = np.floor(np.random.rand(boot_strap_size)*num_samples).astype(int)
    return resample_i


def fill_property_dict(arguments, defaults):
    # Set up properties
    properties = {}
    args_dict = vars(arguments)
    for key in defaults:
        properties[key] = args_dict[key]
        try:
            properties[key] = float(properties[key])
            if int(properties[key]) == properties[key]:
                properties[key] = int(properties[key])
        except ValueError:
            # Value is not an integer
            continue
    return defaults