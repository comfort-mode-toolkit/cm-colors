ColorPair API Reference for CM-Colors
======================================

.. meta::
   :description: Complete API reference for ColorPair class in CM-Colors. Fix single text/background color pairs programmatically in Python.

Complete reference for the ``ColorPair`` class.

Overview
--------

``ColorPair`` fixes a single text/background color pair. Use this when you have one color to fix.

For many colors, use :doc:`make-readable-bulk-api-reference` instead.

Creating a ColorPair
--------------------

.. py:class:: ColorPair(text_color, bg_color, large_text=False)

   Create a color pair to check or fix.

   :param text_color: Text (foreground) color. Accepts hex (``"#rrggbb"``), RGB tuple (``(r, g, b)``), or CSS name (``"red"``).
   :param bg_color: Background color. Same formats as text_color.
   :param large_text: Set to ``True`` if text is large (24px+ or 19px+ bold). Default is ``False``.

   **Examples:**

   .. code-block:: python

      from cm_colors import ColorPair

      # Hex colors
      pair = ColorPair("#777777", "#ffffff")

      # RGB tuples
      pair = ColorPair((119, 119, 119), (255, 255, 255))

      # CSS names
      pair = ColorPair("gray", "white")

      # Large text (headings, buttons)
      pair = ColorPair("#888888", "#ffffff", large_text=True)

Methods
-------

make_readable()
~~~~~~~~~~~~~~~

.. py:method:: ColorPair.make_readable(mode=1, very_readable=False, show=False, save_report=False)

   Fix the text color to make it readable.

   :param mode: How strict to be about changes. ``0``=Strict (minimal changes), ``1``=Default (balanced), ``2``=Relaxed (prioritize readability). Default is ``1``.
   :type mode: int

   :param very_readable: If ``True``, aim for very readable colors. Default is ``False``.
   :type very_readable: bool

   :param show: If ``True``, print a before/after preview to console. Default is ``False``.
   :type show: bool

   :param save_report: If ``True``, generate HTML report (``cm_colors_quick_report.html``). Default is ``False``.
   :type save_report: bool

   :return: Tuple of (fixed_color, success)
   :rtype: tuple

   **Return values:**

   * **fixed_color**: The readable color in same format as input (hex stays hex, tuple stays tuple)
   * **success**: ``True`` if color is now readable, ``False`` otherwise

   **Examples:**

   .. code-block:: python

      from cm_colors import ColorPair

      # Basic usage
      pair = ColorPair("#777777", "#ffffff")
      fixed, success = pair.make_readable()
      # fixed = '#757575', success = True

      # Strict mode (minimal changes)
      fixed, success = pair.make_readable(mode=0)

      # Very readable colors
      fixed, success = pair.make_readable(very_readable=True)

      # Show preview in console
      fixed, success = pair.make_readable(show=True)

      # Generate HTML report
      fixed, success = pair.make_readable(save_report=True)

Properties
----------

is_readable
~~~~~~~~~~~

.. py:attribute:: ColorPair.is_readable

   Check if text is readable on background without fixing.

   :return: ``"Very Readable"``, ``"Readable"``, or ``"Not Readable"``
   :rtype: str

   **Example:**

   .. code-block:: python

      from cm_colors import ColorPair

      pair = ColorPair("#000000", "#ffffff")
      print(pair.is_readable)  # "Very Readable"

      pair2 = ColorPair("#cccccc", "#ffffff")
      print(pair2.is_readable)  # "Not Readable"

      # Use in conditional
      if pair.is_readable == "Not Readable":
          fixed, success = pair.make_readable()

is_valid
~~~~~~~~

.. py:attribute:: ColorPair.is_valid

   Check if both colors are valid.

   :return: ``True`` if both colors parse correctly, ``False`` otherwise
   :rtype: bool

   **Example:**

   .. code-block:: python

      from cm_colors import ColorPair

      pair = ColorPair("#777777", "#ffffff")
      print(pair.is_valid)  # True

      bad_pair = ColorPair("notacolor", "#ffffff")
      print(bad_pair.is_valid)  # False

text and bg
~~~~~~~~~~~

.. py:attribute:: ColorPair.text
.. py:attribute:: ColorPair.bg

   Access the individual colors as ``Color`` objects.

   **Example:**

   .. code-block:: python

      from cm_colors import ColorPair

      pair = ColorPair("#777777", "#ffffff")

      # Get hex
      print(pair.text.to_hex())  # '#777777'
      print(pair.bg.to_hex())    # '#ffffff'

      # Get RGB
      print(pair.text.rgb)  # (119, 119, 119)
      print(pair.bg.rgb)    # (255, 255, 255)

Complete example
----------------

.. code-block:: python

   from cm_colors import ColorPair

   # Check readability first
   pair = ColorPair("#999999", "#ffffff")

   print(f"Readable? {pair.is_readable}")  # "Not Readable"

   if pair.is_readable != "Very Readable":
       # Fix the color
       fixed, success = pair.make_readable(
           mode=1,              # Balanced approach
           very_readable=True,  # Extra readable
           save_report=True     # Generate report
       )

       if success:
           print(f"Use {fixed} instead of #999999")
       else:
           print("Could not fix - too different from original")

See also
--------

* :doc:`how-to-fix-single-color-pair` - How-to guide with examples
* :doc:`make-readable-bulk-api-reference` - For processing many colors
* :doc:`troubleshooting-common-issues` - Solutions to problems
* :doc:`index` - Back to main page
