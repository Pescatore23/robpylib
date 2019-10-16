from distutils.core import setup
setup(name='RobPyLib',
      version='1.0',
      packages=['RobPyLib', 'RobPyLib.CommonFunctions', 'RobPyLib.NetworkGeneration', 'RobPyLib.NetworkGeneration.JeffGostick'],
	  install_requires=['numpy','os','skimage','scipy', 'csv'],
      )