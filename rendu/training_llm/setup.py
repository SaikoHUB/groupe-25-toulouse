"""Setup configuration for Phi-3 Medical Chatbot"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="phi3-medical-chatbot",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Fine-tune Phi-3.5 for medical conversations with Mac Silicon support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/phi3-medical-chatbot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "medical-train=scripts.train:main",
            "medical-inference=scripts.inference:main",
            "medical-check=scripts.setup_check:main",
        ],
    },
)
