from setuptools import setup, find_packages

setup(
    name="sql2erd",
    version="0.1.0",
    packages=find_packages(), 
    install_requires=["graphviz", "sqlparse"],
    entry_points={
        'console_scripts': [
            'my-program=sql2erd.main:main',
        ],
    },
    author="mhdeeb",
    author_email="s-mohamed.eldeeb@zewailcity.edu.eg",
    description="Transforms a .sql file of CREATE TABLE statments into an ERD using Graphviz",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url="https://github.com/mhdeeb/sql2erd",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
