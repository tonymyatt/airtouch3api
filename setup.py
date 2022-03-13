import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="airtouch3",
    version="0.9",
    author="Tony Myatt",
    author_email="tony@myatt.com.au",
    description="API for the monitoring and control of a HVAC unit branded Polyaire Airtouch 3 over a local network",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tonymyatt/airtouch3api",
    project_urls={
        "Bug Tracker": "https://github.com/tonymyatt/airtouch3api/issues",
    },
    packages=setuptools.find_packages(),
    install_requires=[''],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)