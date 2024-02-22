from setuptools import setup

setup(
    name="crossygame",
    version="1.0.0",
    py_modules=["crossygame"],
    entry_points={
        "console_scripts": [
            "crossygame=crossygame:main",
        ],
    },
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
