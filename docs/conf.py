import os
import sys
sys.path.insert(0, os.path.abspath('../'))

# Project information
project = 'Critical Duration Analysis'
copyright = '2025, MIT'
author = 'Daniel Hamill'

# General configuration
extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.mathjax',
    'autoapi.extension'
]

templates_path = ['_templates']
exclude_patterns = []

# HTML output
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
autoapi_dirs = ['../critical_duration']
