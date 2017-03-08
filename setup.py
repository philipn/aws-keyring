from setuptools import setup, find_packages

setup(
    name='aws-keyring',
    version='0.2.5',
    description='Manage AWS credentials in your OS keyring.',
    author='Philip Neustrom',
    author_email='philipn@gmail.com',
    url='http://github.com/philipn/aws-keyring/',
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'keyring==4.0',
        'boto>=2.30',
        'docopt==0.6.2',
        'python-dateutil',
    ],
    entry_points={
        'console_scripts': [
            'aws-keys=aws_keys.__init__:main'
        ]
    },
)
