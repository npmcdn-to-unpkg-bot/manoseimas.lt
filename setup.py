from setuptools import setup, find_packages

setup(
    name='manoseimas-lt',
    version='0.1',
    license='AGPLv3+',
    packages=find_packages(),
    install_requires=[
        'Pillow',
        'django',
        'python-social-auth',
        'sorl-thumbnail',
        'couchdbkit',
        'django-sboard',
        'Scrapy',
        'CouchDB',
        'twisted',
        'pycrypto',
        'django_compressor',
        'MySQL-python',
        'pylibmc',
        'mock',
        'coverage',
        'django-debug-toolbar',
        'django-extensions',
        'django-test-utils',
        'django-webpack-loader',
        'Werkzeug',
        'ipdb',
        'ipython',
        'django-pdb',
        'django-nose',
        'ipdbplugin',
        'exportrecipe',
        'libsass',
        'django-libsass',
        'pyjade',
        'django-autoslug',
        'six',
        'leveldb',
        'tqdm',
        'roman',
        'toposort',
        'django-jsonfield',
        'PyReact',
    ],
    entry_points={
        'console_scripts': [
            'couch = manoseimas.scripts.couch:main',
            'initscrapy = manoseimas.scrapy.main:main',
        ],
    }
)
