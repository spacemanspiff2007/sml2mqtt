import os
import re
import sys
from pathlib import Path


RTD_BUILD = os.environ.get('READTHEDOCS') == 'True'


# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'sml2mqtt'
copyright = '2023, spacemanspiff2007'
author = 'spacemanspiff2007'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx_exec_code',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx_autodoc_typehints',
    'sphinxcontrib.autodoc_pydantic',
]

templates_path = ['_templates']
exclude_patterns = []


# https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-add_module_names
# use class name instead of FQN
add_module_names = False


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['theme_changes.css']


# -- Options for autodoc -------------------------------------------------
autodoc_member_order = 'bysource'
autoclass_content = 'class'

# so autodoc does find the source
sys.path.insert(0, str(Path(__file__).parent.with_name('src')))


# -- Options for autodoc pydantic -------------------------------------------------
# https://autodoc-pydantic.readthedocs.io/en/stable/

# No config on member
autodoc_pydantic_model_show_config_member = False
autodoc_pydantic_model_show_config_summary = False

# No validators
autodoc_pydantic_model_show_validator_summary = False
autodoc_pydantic_model_show_validator_members = False

# Model configuration
autodoc_pydantic_model_signature_prefix = 'settings'
autodoc_pydantic_model_show_json = False
autodoc_pydantic_model_show_field_summary = False
autodoc_pydantic_model_member_order = 'bysource'

# Field config
autodoc_pydantic_field_show_alias = False
autodoc_pydantic_field_list_validators = False
autodoc_pydantic_field_swap_name_and_alias = True

# -- Options for intersphinx -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html
if RTD_BUILD:
    intersphinx_mapping = {
        'python': ('https://docs.python.org/3', None)
    }

# -- Options for nitpick -------------------------------------------------
# Don't show warnings for missing python references since these are created via intersphinx during the RTD build
if not RTD_BUILD:
    nitpick_ignore_regex = [
        (re.compile(r'^py:class'), re.compile(r'pathlib\..+')),
        (re.compile(r'^py:data'), re.compile(r'typing\..+')),
        (re.compile(r'^py:class'), re.compile(r'pydantic\..+|.+Constrained(?:Str|Int|Float)Value')),
    ]
