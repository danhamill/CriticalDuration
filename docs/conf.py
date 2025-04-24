import os
import sys
sys.path.insert(0, os.path.abspath('../'))

# Project information
project = 'Critical Duration Analysis'
copyright = '2025, Your Name'
author = 'Your Name'

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.mathjax',
]

templates_path = ['_templates']
exclude_patterns = []

# HTML output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']