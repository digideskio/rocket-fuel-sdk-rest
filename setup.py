# -*- coding: utf-8 -*-

from setuptools import setup
# from setuptools import find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='rocket-fuel-sdk-rest',
    version='0.1.1',
    description='ExactTarget REST API Wrapper',
    long_description=readme,
    author='JBA',
    author_email='lex@jbadigital.com.com',
    url='https://github.com/jbadigital/rocket-fuel-sdk-rest',
    license=license,
    install_requires=['requests'],
    packages=['rocket_fuel_sdk_rest']
)
