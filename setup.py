# -*- encoding: utf-8 -*-
import glob
import os
import setuptools

setuptools.setup(
    name='plottingscripts',
    description='Code to plot output of various AAD experiments',
    version='0.0.1dev',
    packages=setuptools.find_packages(),
    install_requires=["numpy",
                      "scipy",
                      "matplotlib"
                      ],
    test_requires=["mock"],
    test_suite='nose.collector',
    scripts=glob.glob(os.path.join('scripts', '*.py')),
    author='Katharina Eggensperger',
    author_email='eggenspk@informatik.uni-freiburg.de',
    license='BSD',
    platforms=['Linux']
)
