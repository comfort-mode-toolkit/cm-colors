How to Use Color Contrast Linter
==================================

.. meta::
   :description: Automate accessibility testing with the Color Contrast Linter. Check your design tokens and color pairs for WCAG compliance in your terminal.

Stop checking colors manually. Let the linter do it for you.

The **Color Contrast Linter** is a tool that checks your colors against accessibility standards automatically. It's like a spell-checker, but for color readability.

Installation
------------

Install it with pip:

.. code-block:: bash

   pip install color-contrast-linter

Step 1: Create a config file
----------------------------

Go to your project folder and run:

.. code-block:: bash

   cc-lint init

This creates a file named ``.color_pairs.yml``. This is where you list the colors you want to check.

Step 2: Define your colors
--------------------------

Open ``.color_pairs.yml`` and add your color pairs:

.. code-block:: yaml

   min_contrast: AA
   pairs:
     - foreground: "#000000"
       background: "#ffffff"
     - foreground: "#767676"
       background: "#ffffff"

You can check hex codes, RGB values, or named colors.

**Options:**

* ``min_contrast``: Set to ``AA`` (standard) or ``AAA`` (strict).
* ``pairs``: The list of text (foreground) and background colors to test.

Step 3: Run the check
---------------------

Run the linter:

.. code-block:: bash

   cc-lint lint

You'll see a report in your terminal:

.. code-block:: text

   Checking color contrast...
   
   PASS  #000000 on #ffffff (Ratio: 21.0:1)
   FAIL  #767676 on #ffffff (Ratio: 4.54:1) - Close call!
   
   1 passed, 1 failed.

Fixing failures
---------------

If the linter reports a failure, you have two options:

1. **Fix it automatically**: Use ``cm-colors`` to find a readable version of that color.
   
   .. code-block:: python
   
      from cm_colors import ColorPair
      pair = ColorPair("#767676", "#ffffff")
      fixed, success = pair.make_readable()
      print(fixed)

2. **Update your config**: Paste the new, readable color into your ``.color_pairs.yml`` file.

Why use this?
-------------

* **Catch regressions**: Ensure new design changes don't break accessibility.
* **Design System QA**: Test your core color palette once and never worry again.
* **Documentation**: Your config file serves as a "source of truth" for accessible color pairs.

See also
--------

* :doc:`how-to-add-linter-to-github-actions` - Run this automatically on every Pull Request
* :doc:`how-to-fix-single-color-pair` - Fix colors that fail the lint check