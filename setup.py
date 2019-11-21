from setuptools import setup

with open("README.md", encoding="utf8") as f:
    readme = f.read()

with open("attribution/__init__.py", encoding="utf8") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split('"')[1]

setup(
    name="attribution",
    description="generate changelogs based on tag messages and shortlog",
    long_description=readme,
    long_description_content_type="text/markdown",
    version=version,
    author="John Reese",
    author_email="john@noswap.com",
    url="https://github.com/jreese/attribution",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    license="MIT",
    packages=["attribution", "attribution.tests"],
    package_data={"attribution": ["py.typed"]},
    python_requires=">=3.6",
    setup_requires=["setuptools>=38.6.0"],
    install_requires=["attrs", "click", "jinja2", "packaging"],
    entry_points={"console_scripts": ["attribution = attribution.main:main"]},
)
