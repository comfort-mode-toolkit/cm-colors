import setuptools

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name='cm-colors',
    version='0.2.1',
    author='Lalitha A R',
    author_email='arlalithablogs@gmail.com',
    description='You pick your colors, we make it readable',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/comfort-mode-toolkit/cm-colors',
    project_urls={
        'Documentation': 'https://comfort-mode-toolkit.readthedocs.io/en/latest/cm_colors/installation.html',
        'Bug Reports': 'https://github.com/comfort-mode-toolkit/cm-colors/issues',
        'Source': 'https://github.com/comfort-mode-toolkit/cm-colors',
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Scientific/Engineering',
    ],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(
        where='src', exclude=['cm_colors.cli', 'cm_colors.cli.*']
    ),
    python_requires='>=3.7',
)
