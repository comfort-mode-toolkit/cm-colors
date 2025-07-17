import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cm-colors",
    version="0.0.1",
    author="Lalitha A R",
    author_email="arlalithablogs@gmail.com",
    description="Mathematically Rigorous Accessible Color Science Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/comfort-mode-toolkit/cm-colors",
    project_urls={
        "Documentation": "https://github.com/comfort-mode-toolkit/cm-colors",
        "Bug Reports": "https://github.com/comfort-mode-toolkit/cm-colors/issues",
        "Source": "https://github.com/comfort-mode-toolkit/cm-colors",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Scientific/Engineering",
    ],
    package_dir={"": "."}, # Look for packages in the current directory
    py_modules=["main", "helper", "accessible_palatte"], # List your .py files as modules
    python_requires=">=3.7", # Minimum Python version required
)

