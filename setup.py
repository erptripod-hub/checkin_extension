from setuptools import setup, find_packages

setup(
    name="checkin_extension",
    version="1.0.0",
    author="Your Company",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["frappe"],
)
