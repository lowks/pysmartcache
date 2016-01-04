from setuptools import setup

VERSION = '0.7.2'


setup(
    name='pysmartcache',
    packages=['pysmartcache', ],
    version=VERSION,
    author='Filipe Waitman',
    author_email='filwaitman@gmail.com',
    description='PySmartCache is a way to get automatic caching and caching invalidation for functions/methods.',
    install_requires=[x.strip() for x in open('requirements.txt').readlines()],
    tests_require=[x.strip() for x in open('requirements_test.txt').readlines()],
    url='https://github.com/filwaitman/pysmartcache',
    download_url='https://github.com/filwaitman/pysmartcache/tarball/{}'.format(VERSION),
    keywords=['cache', 'caching', 'memcached', 'redis', 'memoization', 'memoize'],
    test_suite='tests',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Operating System :: OS Independent",
    ]
)
