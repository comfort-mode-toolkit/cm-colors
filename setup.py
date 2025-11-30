from setuptools import setup, find_packages


with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='cm-colors',
    version='0.5.0',
    author='Lalitha A R',
    author_email='arlalithablogs@gmail.com',
    description='Automatically fix hard-to-read text colors by making your website readable without changing your original color theme—simple Python API and CLI.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/comfort-mode-toolkit/cm-colors',
    project_urls={
        'Documentation': 'https://comfort-mode-toolkit.readthedocs.io/en/latest/cm_colors/index.html',
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
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Utilities',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
        'Topic :: Scientific/Engineering',
    ],
    package_dir={'': 'src'},
    packages=find_packages(
        where='src'
    ),  # Updated to use find_packages directly
    install_requires=[  # Added install_requires
        'tinycss2>=1.2.0,<2.0.0',
        'click>=8.0.0,<9.0.0',
        'rich>=10.0.0',
    ],
    entry_points={
        'console_scripts': [
            'cm-colors=cm_colors.cli.main:main',
        ],
    },
    python_requires='>=3.7',
    keywords=[
        'accessibility',
        'color-contrast',
        'wcag',
        'a11y',
        'css-colors',
        'automated-accessibility',
        'color-fixing',
        'contrast-tuning',
        'readable',
        'legible',
    ],
)
