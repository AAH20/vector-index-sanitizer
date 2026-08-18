from setuptools import setup, find_packages

setup(
    name="vector-index-sanitizer",
    version="1.0.0",
    description="Vector Database Index Poisoning & Synthetic Contamination Firewall",
    author="Ahmed Hassan",
    author_email="ahmed.alaa.hassan25@gmail.com",
    packages=find_packages(),
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
