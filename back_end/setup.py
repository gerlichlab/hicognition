import setuptools

with open('VERSION') as version_file:
   version_number = version_file.read().strip()


setuptools.setup(
    name="hicognition",
    version = version_number,
    packages=["hicognition"],
    install_requires=["pandas", "bioframe", "pandas", "requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
