# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'cm-colors'
copyright = '2025, Lalitha A R'
author = 'Lalitha A R'
release = 'v0.5.0'

html_title = 'cm-colors: Make Text Readable'
html_short_title = 'cm-colors'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # ... other extensions
    "sphinx_copybutton",
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


html_theme = 'furo'

pygments_style = "friendly"
pygments_dark_style = "github-dark"

html_static_path = ['_static']

html_file_options = {
    'description': 'Automatically fix hard-to-read text colors by making your website readable without changing your original color theme—simple Python API and CLI.',
    'dark_mode_toggle': True,
}

# extensions = [
# 'myst_parser',  # For Markdown support
#     'sphinx_design',
# ]

# html_theme_options.update({
#     "source_repository": "https://github.com/comfort-mode-toolkit/cm-colors/",
#     "source_branch": "main",
#     "source_dir": "docs",  # code-heavy → always show edit links
#     "footer_icons": [     # credibility signals
#         {
#             "name": "GitHub",
#             "url": "https://github.com/comfort-mode-toolkit/cm-colors",
#             "html": '<img src="github.svg"/>',
#             "class": "",
#         }
#     ],
# })
