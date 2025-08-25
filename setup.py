from setuptools import setup, find_packages

setup(
    name="rt_academy",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "streamlit",
        "plotly",
        "numpy",
    ],
)
