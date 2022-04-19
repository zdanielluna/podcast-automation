from setuptools import setup


setup(
    name='cli',
    version='0.1.0',
    py_modules=['cli'],
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'botcast=cli.cli:botcast',
            'mbotcast=cli.cli:mbotcast',
            'mbotcast-init=cli.cli:init',
        ],
    },
)
