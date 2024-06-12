from setuptools import setup, find_packages


with open("README.md") as f:
    readme = f.read()

with open("LICENSE") as f:
    license = f.read()

setup(
    name="ip-cam-recoder",
    version="0.1.0",
    description="IP Camera streams recoder",
    long_description=readme,
    author="Buddhika Abeysekera",
    author_email="babey.lk@gmail.com",
    url="https://github.com/mbabeysekera",
    license=license,
    packages=find_packages(exclude=("tests", "docs")),
)
