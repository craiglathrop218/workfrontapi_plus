from setuptools import setup, find_packages

version = '1.0.23'

setup(
        name='workfrontapi_plus',

        version=version,

        description='A Python 3 compatible package for working with the Workfront API',
        long_description='This packages is designed to help interface with the Workfront API with features such as making '
                         'an update on behalf of another user, support for lists in parameters, returning more than 2000'
                         'items in a search.',

        url='https://github.com/craiglathrop218/workfrontapi_plus',
        download_url='https://github.com/craiglathrop218/workfrontapi_plus/archive/'+version+'.tar.gz',

        author='Roshan Bal, Craig Lathrop',
        author_email='none@none.com',

        license='MIT',

        classifiers=[
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 5 - Production/Stable',

            'Intended Audience :: Developers',

            'License :: OSI Approved :: MIT License',

            # Supported versions
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
        ],
        keywords='Workfront API AtTask',
        packages=find_packages(),
        install_requires=['requests'],

)