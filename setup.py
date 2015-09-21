from distutils.core import setup

setup(
    name='rhobot',
    version='1.0.0',
    packages=[
        'rhobot',
        'rhobot.components',
        'rhobot.components.commands',
        'rhobot.components.stanzas',
        'rhobot.components.storage',
        'rhobot.components.storage.payload',
    ],
    url='',
    license='BSD',
    author='Robert Robinson',
    author_email='rerobins@meerkatlabs.org',
    description='Rhobot Core',
    install_requires=[
        'sleekxmpp==1.4.0.dev0',
        'rdflib==4.2.0',
        'enum34==1.0.4'],
    dependency_links=[
        'https://github.com/rerobins/SleekXMPP/tarball/rhobot#egg=sleekxmpp-1.4.0.dev0',
    ],
    scripts=['bin/rho', 'bin/rho_daemon']
)
