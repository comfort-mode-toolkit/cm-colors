Fix Unreadable Colors in Python
=================================

.. meta::
   :description: Check color contrast and make text readable in seconds. Run local checks, automate accessibility in CI/CD, and instantly fix failing color pairs with Python or CLI.

Make your text readable for everyone.

Quick Start
-----------

**Fix a hard-to-read color:**

.. code-block:: python

   from cm_colors import ColorPair
   
   # 1. Define the problem
   pair = ColorPair("#777777", "#ffffff")
   
   # 2. Get the solution
   fixed_color, success = pair.make_readable()
   
   print(fixed_color) 
   # Output: #757575 (Readable!)

**Check your project:**

.. code-block:: bash

   # Run the linter
   cc-lint lint

Installation
------------

.. code-block:: bash

   pip install cm-colors

How to use it
-------------

Follow these steps to ensure your colors work for everyone:

1. **Check Locally**
   
   Run the linter in your terminal to catch issues while you work.
   
   * :doc:`how-to-use-color-contrast-linter`

2. **Automate Checks**
   
   Stop bad colors from being merged by adding a check to GitHub Actions.
   
   * :doc:`how-to-add-linter-to-github-actions`

3. **Fix the Issues**
   
   When you find a problem, use our tools to fix it automatically.
   
   * :doc:`how-to-fix-single-color-pair` - Fix one pair in Python
   * :doc:`how-to-fix-multiple-colors-bulk` - Fix lists of colors
   * :doc:`how-to-fix-colors-in-css-files` - Fix CSS files automatically

Deep Dive
---------

* :doc:`what-makes-cm-colors-work` - The science of preserving your design
* :doc:`accessibility-explained` - Mapping "Readable" to standards

Research
--------

The algorithm is described in two papers:

* `Context-Adaptive Color Optimization for Web Accessibility <https://arxiv.org/abs/2512.07623>`_ (arXiv:2512.07623) — 93.68% success across 10,000 random branding-representative pairs, 100% on pairs with initial contrast ratio > 2.0.
* `Perceptually-Minimal Color Optimization for Web Accessibility <https://arxiv.org/abs/2512.05067>`_ (arXiv:2512.05067) — the multi-phase OKLCH + CIEDE2000 approach.

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Check & Automate

   how-to-check-color-contrast-in-terminal
   how-to-use-color-contrast-linter
   how-to-add-linter-to-github-actions

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Fix Colors

   how-to-fix-single-color-pair
   how-to-fix-multiple-colors-bulk
   how-to-fix-colors-in-css-files
   recipes/use-without-programming

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Understand

   what-makes-cm-colors-work
   accessibility-explained
   understanding-readability-levels

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Reference

   colorpair-api-reference
   make-readable-bulk-api-reference
   troubleshooting-common-issues
