from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cm-colors",
    version="1.0.0",
    author="Lalitha A R",
    author_email="arlalithablogs@gmail.com",
    description="Mathematically rigorous accessible color science library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/comfort-mode-toolkit/cm-colors",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Human Machine Interfaces",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "pdf": ["reportlab>=3.6.0"],
        "dev": ["pytest>=6.0", "black", "flake8", "mypy"],
    },
    keywords=[
        "accessibility", "color", "wcag", "contrast", "oklch", "delta-e",
        "color-science", "design-systems", "brand-colors", "inclusive-design"
    ],
    project_urls={
        "Documentation": "https://github.com/comfort-mode-toolkit/cm-colors",
        "Bug Reports": "https://github.com/comfort-mode-toolkit/cm-colors",
        "Source": "https://github.com/comfort-mode-toolkit/cm-colors",
    },
)