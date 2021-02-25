import setuptools
import os

#with open(os.path.join(os.pardir, 'VERSION')) as version_file:
#   version_number = version_file.read().strip()
# TODO why does this not work?

setuptools.setup(
    name="hicognition",
    version = "0.2",
    #version = version_number
    packages=["hicognition"],
    install_requires=["pandas", "bioframe", "pandas", "requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
