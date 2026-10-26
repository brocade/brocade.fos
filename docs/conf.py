# Copyright 2019-2026 Broadcom. All rights reserved.
# The term 'Broadcom' refers to Broadcom Inc. and/or its subsidiaries
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt) AND BSD-2-Clause
# SPDX-License-Identifier: GPL-3.0-or-later AND BSD-2-Clause

# Copyright (c) Ansible Project
# GNU General Public License v3.0+ (see LICENSES/GPL-3.0-or-later.txt or https://www.gnu.org/licenses/gpl-3.0.txt)
# SPDX-License-Identifier: GPL-3.0-or-later

# Created with antsibull-docs 2.24.0

# This file only contains a selection of the most common options. For a full list see the
# documentation:
# http://www.sphinx-doc.org/en/master/config

project = "Ansible collections"
copyright = "Ansible contributors"

title = "Ansible Collections Documentation"
html_short_title = "Ansible Collections Documentation"

extensions = ["sphinx.ext.autodoc", "sphinx.ext.intersphinx", "sphinx_antsibull_ext", "myst_parser"]

pygments_style = "ansible"

highlight_language = "YAML+Jinja"

html_theme = "sphinx_ansible_theme"
html_show_sphinx = False

display_version = False

html_use_smartypants = True
html_use_modindex = False
html_use_index = False
html_copy_source = False

intersphinx_mapping = {
    "ansible_devel": ("https://docs.ansible.com/projects/ansible/devel/", None),
}

suppress_warnings = ["misc.highlighting_failure"]

default_role = "any"

nitpicky = True
