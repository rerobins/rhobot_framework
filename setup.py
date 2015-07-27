from distutils.core import setup

setup(
    name='rhobot',
    version='1.0.0',
    packages=['rhobot', 'rhobot.components'],
    url='',
    license='BSD',
    author='Robert Robinson',
    author_email='rerobins@meerkatlabs.org',
    description='Rhobot Core',
    install_requires=['sleekxmpp==1.3.1', 'rdflib==4.2.0']
)
