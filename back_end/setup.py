import setuptools

setuptools.setup(
    name="hicognition",
    version="0.1.0",
    packages=setuptools.find_packages(),
    install_requires=["pandas", "bioframe", "pandas", "requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
