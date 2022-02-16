"""Installs the hicognition package."""
import setuptools

with open("VERSION", encoding="utf-8") as version_file:
    version_number = version_file.read().strip()


setuptools.setup(
    name="hicognition",
    version=version_number,
    packages=["hicognition"],
    install_requires=["pandas", "bioframe", "pandas", "requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
