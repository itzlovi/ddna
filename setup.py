from setuptools import setup, find_packages

setup(
    name="digital-dna",
    version="0.1.0",
    description="Continuous Multimodal Behavioral Biometrics for Continuous Authentication",
    author="Lovepreet",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "pynput>=1.7.6",
        "psutil>=5.9.0",
        "numpy>=1.24.0",
        "scipy>=1.10.0",
        "scikit-learn>=1.3.0",
        "joblib>=1.3.0",
        "pandas>=2.0.0",
        "PyQt6>=6.5.0",
    ],
    entry_points={
        "console_scripts": [
            "ddna=app.desktop.main:main",
        ],
    },
)
