from setuptools import setup, find_packages

setup(
    name='CriticalDuration',
    version='0.1.0',
    author='Daniel Hamill',
    author_email='Daniel.D.Hamill@usace.army.mil',
    description='A package for analyzing critical duration events in hydrological data.',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'pydsstools',
        'altair',
        'openpyxl',
        "pytest"
    ],
    entry_points={
        'console_scripts': [
            'run_analysis=scripts.run_analysis:main',
        ],
    },
)