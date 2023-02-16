from setuptools import setup

setup(
    name='beets-yapl',
    version='0.1.2',
    description='beets plugin to handle yaml playlists',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='Nicholas Boyd Isacsson',
    author_email='nicholas@isacsson.se',
    url='http://www.github.com/nichobi/beets-yapl',
    license='GPL3',
    platforms='ALL',

    test_suite='test',

    packages=['beetsplug'],

    install_requires=[
        'beets>=1.4.7',
    ],

    classifiers=[
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Players :: MP3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Environment :: Console',
        'Programming Language :: Python :: 3',
    ],
    )

