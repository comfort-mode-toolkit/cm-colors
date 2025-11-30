Fix Unreadable Colors in Python
==================================

.. meta::
   :description: Make your text colors readable while keeping them visually similar to the original. No accessibility knowledge required. Works with hex, RGB, and any color format.

Make text readable on any background. Keep colors visually similar.

Quick fixes
-----------

**Problem**: Text is hard to read

.. code-block:: python

   from cm_colors import ColorPair
   
   pair = ColorPair("#777777", "#ffffff")
   readable_color, success = pair.make_readable()
   # Use readable_color instead of #777777

**Problem**: Need to fix many colors

.. code-block:: python

   from cm_colors import make_readable_bulk
   
   pairs = [
       ("#777", "#fff"),
       ("#888", "#000"),
       ((100, 100, 100), (255, 255, 255)),
   ]
   results = make_readable_bulk(pairs)
   # [(fixed_color, "readable"), ...]

**Problem**: Have colors in CSS files

.. code-block:: bash

   cm-colors path/to/styles.css

When to use this
----------------

* If you have text that's hard to read on its background
* If PM assigned you an accessibility ticket
* If accessibility or color contrast ticket is in your backlog
* If you found theme that's really good but isn't readable or isn't passing color contrast tests
* If users created an issue about low contrast
* If you want to keep brand colors but make them readable
.. * If you need to fix entire color palette to make it more readable
* If you need to fix entire color palette to pass color contrast tests but keep the colors as similar as possible to the original

What you get
------------

* Colors that are readable
* Original colors preserved as much as possible
* Works with hex codes, RGB tuples, CSS color names
* Bulk processing for multiple colors
* HTML reports showing before/after
* Preview changes right in the terminal
* Use mode=0 to be more strict with color changes if that's needed

How-to guides
-------------

* :doc:`how-to-fix-single-color-pair` - Fix one color (takes 2 lines)
* :doc:`how-to-fix-multiple-colors-bulk` - Fix many colors at once
* :doc:`how-to-fix-colors-in-css-files` - Fix CSS files from command line

API reference
-------------

* :doc:`colorpair-api-reference` - ColorPair class for single colors
* :doc:`make-readable-bulk-api-reference` - Bulk processing function

Help
----

* :doc:`troubleshooting-common-issues` - Solutions to common problems
* :doc:`understanding-readability-levels` - What "readable" means

.. toctree::
   :hidden:
   :maxdepth: 2

   how-to-fix-single-color-pair
   how-to-fix-multiple-colors-bulk
   how-to-fix-colors-in-css-files
   colorpair-api-reference
   make-readable-bulk-api-reference
   troubleshooting-common-issues
   understanding-readability-levels
