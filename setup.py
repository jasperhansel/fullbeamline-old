#!/usr/bin/env python3


from distutils.core import setup


setup(
    name = 'fullbeamline',
    version = '1.0',
    description = 'full beamline simulations using GPT and Bmad',
    author='Jasper Hansel',
    author_email = 'jasperhansel@gmail.com',
    packages=['fullbeamline'],
    scripts=['scripts/fullbeamline'],
    package_data={'fullbeamline': ['fortran/*.f90']}
)
