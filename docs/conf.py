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
    "sphinx_copybutton",
    'sphinxcontrib.googleanalytics',
    "sphinx_sitemap"
]


googleanalytics_id = "G-YK8NDXS8YW"

templates_path = ['_templates']
html_css_files = ['custom.css']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


html_theme = 'furo'

pygments_style = "friendly"
pygments_dark_style = "github-dark"

html_static_path = ['_static']
html_favicon = "_static/logo.png"


html_file_options = {
    'description': 'Automatically fix hard-to-read text colors by making your website readable without changing your original color theme—simple Python API and CLI.',
    'dark_mode_toggle': True,
}

html_meta = {
    'description': 'Check color contrast and make text readable in seconds. Run local checks, automate accessibility in CI/CD, and instantly fix failing color pairs with Python or CLI.',
    'keywords': 'check color contrast, make text readable, fix color contrast issues, WCAG compliance, accessibility',
    'author': 'Lalitha A R & Contributors to cm-colors',
    'viewport': 'width=device-width, initial-scale=1',
    'robots': 'index, follow'
}

extensions.append('sphinxext.opengraph')
ogp_site_url = 'https://cm-colors.readthedocs.io/'
ogp_image = '_static/logo.png'

html_baseurl = 'https://cm-colors.readthedocs.io/en/latest/'
sitemap_filename = 'sitemap.xml'
