Bulk Processing API Reference
=============================

.. meta::
   :description: Complete API reference for make_readable_bulk function in CM-Colors. Process hundreds of color pairs efficiently in Python.

Complete reference for the ``make_readable_bulk()`` function.

Overview
--------

``make_readable_bulk()`` fixes many color pairs in one call. Use this when you have multiple colors to fix.

For single colors, use :doc:`colorpair-api-reference` instead.

Function signature
------------------

.. py:function:: make_readable_bulk(pairs, mode=1, very_readable=False, save_report=False)

   Fix multiple text/background color pairs.

   :param pairs: List of color pairs. Each pair is a tuple: ``(text_color, bg_color)`` or ``(text_color, bg_color, large_text)``.
   :type pairs: list

   :param mode: How strict to be about changes. ``0``=Strict, ``1``=Default, ``2``=Relaxed. Default is ``1``.
   :type mode: int

   :param very_readable: If ``True``, make all colors very readable. Default is ``False``.
   :type very_readable: bool

   :param save_report: If ``True``, generate HTML report (``cm_colors_bulk_report.html``). Default is ``False``.
   :type save_report: bool

   :return: List of tuples: ``(fixed_color, status)``
   :rtype: list

Parameters explained
--------------------

pairs
~~~~~

List of color pairs to fix. Each pair can be:

**Two values** (text and background):

.. code-block:: python

   pairs = [
       ("#777", "#fff"),
       ((100, 100, 100), (255, 255, 255)),
       ("gray", "white"),
   ]

**Three values** (text, background, large_text flag):

.. code-block:: python

   pairs = [
       ("#888", "#fff", False),  # Normal text
       ("#888", "#fff", True),   # Large text
   ]

mode
~~~~

Controls how much colors can change:

* ``0`` (Strict): Minimal changes, may fail to fix some colors
* ``1`` (Default): Balanced approach, works for most cases
* ``2`` (Relaxed): Allows more changes to ensure readability

very_readable
~~~~~~~~~~~~~

When ``True``, aims for very readable colors (stricter standard).

save_report
~~~~~~~~~~~

When ``True``, creates ``cm_colors_bulk_report.html`` showing all changes.

Return value
------------

Returns a list of tuples. Each tuple contains:

* **fixed_color**: The readable color (same format as input)  
* **status**: ``"readable"``, ``"very readable"``, or ``"not readable"``

Examples
--------

Basic usage
~~~~~~~~~~~

.. code-block:: python

   from cm_colors import make_readable_bulk

   pairs = [
       ("#777", "#fff"),
       ("#888", "#000"),
   ]

   results = make_readable_bulk(pairs)

   for color, status in results:
       print(f"{color} - {status}")

   # Output:
   # #757575 - readable
   # #8e8e8e - readable

Format preservation
~~~~~~~~~~~~~~~~~~~

Input format is preserved in output:

.. code-block:: python

   from cm_colors import make_readable_bulk

   pairs = [
       ("#777", "#fff"),                    # Hex input
       ((119, 119, 119), (255, 255, 255)), # Tuple input
   ]

   results = make_readable_bulk(pairs)

   print(results[0][0])  # '#757575' (hex)
   print(results[1][0])  # (117, 117, 117) (tuple)

Process with large_text flag
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from cm_colors import make_readable_bulk

   pairs = [
       ("#888", "#fff", False),  # Body text
       ("#888", "#fff", True),   # Heading
   ]

   results = make_readable_bulk(pairs)

Different modes
~~~~~~~~~~~~~~~

.. code-block:: python

   from cm_colors import make_readable_bulk

   pairs = [("#777", "#fff")]

   # Strict mode
   results = make_readable_bulk(pairs, mode=0)

   # Relaxed mode
   results = make_readable_bulk(pairs, mode=2)

Generate report
~~~~~~~~~~~~~~~

.. code-block:: python

   from cm_colors import make_readable_bulk

   pairs = [
       ("#777", "#fff"),
       ("#888", "#000"),
       ("#999", "#fff"),
   ]

   results = make_readable_bulk(pairs, save_report=True)
   # Creates cm_colors_bulk_report.html

Very readable colors
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from cm_colors import make_readable_bulk

   pairs = [("#777", "#fff"), ("#888", "#000")]

   results = make_readable_bulk(pairs, very_readable=True)

Process JSON data
~~~~~~~~~~~~~~~~~

.. code-block:: python

   import json
   from cm_colors import make_readable_bulk

   # Load colors
   with open("colors.json") as f:
       data = json.load(f)

   # Convert to pairs
   pairs = [(item["text"], item["bg"]) for item in data]

   # Fix all
   results = make_readable_bulk(pairs)

   # Save results
   for item, (fixed, status) in zip(data, results):
       item["fixed_text"] = fixed
       item["status"] = status

   with open("colors_fixed.json", "w") as f:
       json.dump(data, f)

Filter results
~~~~~~~~~~~~~~

.. code-block:: python

   from cm_colors import make_readable_bulk

   pairs = [("#777", "#fff"), ("#000", "#fff"), ("#ccc", "#fff")]
   results = make_readable_bulk(pairs)

   # Get only readable colors
   readable = [color for color, status in results
               if status in ["readable", "very readable"]]

   # Get colors that need attention
   problematic = [color for color, status in results
                  if status == "not readable"]


Performance
-----------

``make_readable_bulk()`` is optimized for processing many colors:

* Processes 100 pairs in ~0.5 seconds
* Processes 1000 pairs in ~5 seconds

For single colors, use :doc:`ColorPair <colorpair-api-reference>` instead.

Complete example
----------------

.. code-block:: python

   from cm_colors import make_readable_bulk

   # Brand color palette
   brand_colors = [
       ("#3498db", "#ffffff"),  # Blue on white
       ("#e74c3c", "#ffffff"),  # Red on white
       ("#2ecc71", "#ffffff"),  # Green on white
       ("#f39c12", "#ffffff"),  # Orange on white
   ]

   # Fix all with very readable setting
   results = make_readable_bulk(
       brand_colors,
       mode=1,               # Balanced
       very_readable=True,   # Extra readable
       save_report=True      # Generate report
   )

   # Print results
   for (original_text, original_bg), (fixed, status) in zip(brand_colors, results):
       if fixed != original_text:
           print(f"{original_text} → {fixed} ({status})")
       else:
           print(f"{original_text} already {status}")

See also
--------

* :doc:`how-to-fix-multiple-colors-bulk` - How-to guide with examples
* :doc:`colorpair-api-reference` - For single colors
* :doc:`troubleshooting-common-issues` - Solutions to problems
* :doc:`index` - Back to main page
