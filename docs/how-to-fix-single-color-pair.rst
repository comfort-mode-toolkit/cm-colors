How to Fix a Single Color Pair
===============================

.. meta::
   :description: Fix one text/background color pair that's hard to read. Takes 2 lines of Python code. Works with hex codes, RGB tuples, and CSS color names.

Fix one text color that's hard to read on its background.

The problem
-----------

You have a text color and background color. The text is hard to read.

The solution
------------

Use ``ColorPair`` and call ``make_readable()``:

.. code-block:: python

   from cm_colors import ColorPair
   
   pair = ColorPair("#777777", "#ffffff")
   readable_color, success = pair.make_readable()
   
   # Use readable_color instead of #777777
   print(readable_color)  # '#757575'

How it works
------------

1. Create a ``ColorPair`` with your text and background colors
2. Call ``make_readable()`` to get a fixed color
3. Use the fixed color in your design

The function returns two values:

* **readable_color**: The fixed color (same format as your input)
* **success**: ``True`` if the color is now readable

Real examples
-------------

Fix hex colors
~~~~~~~~~~~~~~

.. code-block:: python

   from cm_colors import ColorPair
   
   pair = ColorPair("#999999", "#ffffff")
   fixed, success = pair.make_readable()
   # fixed is '#8e8e8e' (darker gray)

Fix RGB tuples
~~~~~~~~~~~~~~

.. code-block:: python

   from cm_colors import ColorPair
   
   text = (150, 150, 150)
   bg = (255, 255, 255)
   
   pair = ColorPair(text, bg)
   fixed, success = pair.make_readable()
   # fixed is (142, 142, 142) - preserves tuple format

Check if colors already readable
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from cm_colors import ColorPair
   
   pair = ColorPair("#000000", "#ffffff")
   
   if pair.is_readable == "Very Readable":
       print("Colors are good")
   else:
       fixed, success = pair.make_readable()
       print(f"Use {fixed} instead")

Large text (bigger fonts)
~~~~~~~~~~~~~~~~~~~~~~~~~

If your text is large (24px or bigger, or 19px+ bold), tell the function:

.. code-block:: python

   from cm_colors import ColorPair
   
   # For headings, large buttons, etc.
   pair = ColorPair("#888888", "#ffffff", large_text=True)
   fixed, success = pair.make_readable()

Want very readable colors
~~~~~~~~~~~~~~~~~~~~~~~~~

For extra readability:

.. code-block:: python

   from cm_colors import ColorPair
   
   pair = ColorPair("#777", "#fff")
   fixed, success = pair.make_readable(very_readable=True)

Common issues
-------------

**"Colors changed too much"**

Use strict mode to minimize changes:

.. code-block:: python

   fixed, success = pair.make_readable(mode=0)

**"Have many colors to fix"**

Use the bulk function instead: :doc:`how-to-fix-multiple-colors-bulk`

**"Need a report showing changes"**

Generate an HTML report:

.. code-block:: python

   fixed, success = pair.make_readable(save_report=True)
   # Creates cm_colors_quick_report.html

See also
--------

* :doc:`how-to-fix-multiple-colors-bulk` - Fix many colors at once
* :doc:`colorpair-api-reference` - Full API reference
* :doc:`troubleshooting-common-issues` - More solutions
* :doc:`index` - Back to main page
