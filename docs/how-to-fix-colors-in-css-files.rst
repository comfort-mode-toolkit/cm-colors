How to Fix Colors in CSS Files
===============================

.. meta::
   :description: Automatically fix all color contrast issues in your CSS files from command line. Works with any CSS file. Creates backup automatically.

Fix all color problems in your CSS files automatically.

The problem
-----------

You have CSS files with hard-to-read colors. You need to fix them all.

The solution
------------

Run the ``cm-colors`` command on your CSS file:

.. code-block:: bash

   cm-colors path/to/styles.css

This creates ``styles_cm.css`` with fixed colors.

How it works
------------

1. The tool reads your CSS file
2. Finds all text/background color pairs
3. Fixes colors that are hard to read
4. Saves results to a new file (``_cm.css``)
5. Your original file stays unchanged

Real examples
-------------

Fix one CSS file
~~~~~~~~~~~~~~~~

.. code-block:: bash

   cm-colors styles.css

Creates ``styles_cm.css`` with readable colors.

Fix all CSS in a directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   cm-colors src/styles/

Processes all ``.css`` files in ``src/styles/`` and subdirectories.

Change background color assumption
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, assumes white background. Change it:

.. code-block:: bash

   cm-colors styles.css --default-bg "#1e1e1e"

For dark themes or non-white backgrounds.

Control how much colors change
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use different modes:

.. code-block:: bash

   # Strict mode - minimal changes
   cm-colors styles.css --mode 0
   
   # Default mode - balanced (default)
   cm-colors styles.css --mode 1
   
   # Relaxed mode - prioritize readability
   cm-colors styles.css --mode 2

Make colors very readable
~~~~~~~~~~~~~~~~~~~~~~~~~~

For extra readability:

.. code-block:: bash

   cm-colors styles.css --premium

What the tool shows
-------------------

After running, you see:

.. code-block:: text

   ✓ 15 color pairs already readable
   ✓ 8 color pairs adjusted for better readability
   ✗ 2 color pairs need your attention
   
   Report generated: cm_colors_report.html

* **Already readable**: No changes needed
* **Adjusted**: Fixed automatically
* **Need attention**: Couldn't fix (too different from original)

Review the HTML report to see all changes.

Common issues
-------------

**"Changes CSS variables"**

The tool updates CSS variable definitions:

.. code-block:: css

   /* Before */
   :root {
     --text-gray: #999999;
   }
   
   /* After */
   :root {
     --text-gray: #8e8e8e;  /* Made readable */
   }

**"Want to fix colors in place"**

Copy the ``_cm.css`` file over your original:

.. code-block:: bash

   cm-colors styles.css
   cp styles_cm.css styles.css

**"Need to process many files"**

Use a loop:

.. code-block:: bash

   for file in src/**/*.css; do
       cm-colors "$file"
   done

Installation
------------

If you don't have cm-colors installed:

.. code-block:: bash

   pip install cm-colors

See also
--------

* :doc:`how-to-fix-single-color-pair` - Fix colors in Python code
* :doc:`how-to-fix-multiple-colors-bulk` - Bulk processing in Python
* :doc:`troubleshooting-common-issues` - Solutions to problems
* :doc:`index` - Back to main page
