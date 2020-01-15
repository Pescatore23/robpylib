from setuptools import setup, find_packages

setup(name='robpylib',
      version='1.0',
      packages=find_packages(),
      install_requires=['numpy','scikit-image','scipy', 'astropy', 'pandas', 'pystackreg'],
      )
