from distutils.core import setup

setup(
      name='Pidra',
      version='0.1',
      description='Basic home automation library',
      author='Teska',
      packages=['pidra', 'pidra.interfaces', 'pidra.tivo'],
      requires=['requests']
)