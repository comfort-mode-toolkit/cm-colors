How to Fix Multiple Colors at Once
===================================

.. meta::
   :description: Fix dozens or hundreds of color pairs efficiently in Python. Perfect for entire color palettes. Returns all fixed colors with readability status.

Fix many text/background color pairs in one go.

The problem
-----------

You have many color pairs to fix. Calling ``ColorPair`` for each one is tedious.

The solution
------------

Use ``make_readable_bulk()`` to process all pairs at once:

.. code-block:: python

   from cm_colors import make_readable_bulk
   
   pairs = [
       ("#777",  "#fff"),
       ("#888", "#000"),
       ("#999", "#fff"),
   ]
   
   results = make_readable_bulk(pairs)
   
   for fixed_color, status in results:
       print(f"{fixed_color} - {status}")

Output:

.. code-block:: text

   #757575 - readable
   #8e8e8e - readable  
   #979797 - readable

How it works
------------

1. Create a list of color pairs (tuples)
2. Call ``make_readable_bulk()`` with the list
3. Get back a list of (fixed_color, status) tuples

Each result contains:

* **fixed_color**: The readable color (same format as input)
* **status**: "readable", "very readable", or "not readable"

Real examples
-------------

Fix website color palette
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from cm_colors import make_readable_bulk
   
   # Your brand colors on white background
   brand_colors = [
       ("#3498db", "#ffffff"),  # Blue
       ("#e74c3c", "#ffffff"),  # Red
       ("#2ecc71", "#ffffff"),  # Green
       ("#f39c12", "#ffffff"),  # Orange
   ]
   
   results = make_readable_bulk(brand_colors)
   
   for original, (fixed, status) in zip(brand_colors, results):
       print(f"{original[0]} → {fixed} ({status})")

Mix different color formats
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can use hex, RGB tuples, or CSS names in the same list:

.. code-block:: python

   from cm_colors import make_readable_bulk
   
   mixed_pairs = [
       ("#777", "#fff"),                    # Hex
       ((100, 100, 100), (255, 255, 255)), # RGB tuples
       ("gray", "white"),                   # CSS names
   ]
   
   results = make_readable_bulk(mixed_pairs)
   # Each result preserves its input format

Large text in bulk
~~~~~~~~~~~~~~~~~~

Mark which pairs use large text with a third value:

.. code-block:: python

   from cm_colors import make_readable_bulk
   
   pairs = [
       ("#888", "#fff", False),  # Normal text
       ("#888", "#fff", True),   # Large text (headings, etc.)
       ("#999", "#000"),         # Normal text (default)
   ]
   
   results = make_readable_bulk(pairs)

Get an HTML report
~~~~~~~~~~~~~~~~~~

See all changes in a visual report:

.. code-block:: python

   from cm_colors import make_readable_bulk
   
   pairs = [
       ("#777", "#fff"),
       ("#888", "#000"),
       ("#999", "#fff"),
   ]
   
   results = make_readable_bulk(pairs, save_report=True)
   # Creates cm_colors_bulk_report.html

Want very readable colors
~~~~~~~~~~~~~~~~~~~~~~~~~

Make all colors very readable:

.. code-block:: python

   results = make_readable_bulk(pairs, very_readable=True)

Control how much colors change
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use different modes:

.. code-block:: python

   # Strict - minimal changes
   results = make_readable_bulk(pairs, mode=0)
   
   # Default - balanced
   results = make_readable_bulk(pairs, mode=1)
   
   # Relaxed - prioritize readability
   results = make_readable_bulk(pairs, mode=2)

Common patterns
---------------

Process JSON color data
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   import json
   from cm_colors import make_readable_bulk
   
   # Load colors from JSON
   with open("colors.json") as f:
       data = json.load(f)
   
   # Convert to pairs list
   pairs = [(item["text"], item["bg"]) for item in data["colors"]]
   
   # Fix all colors
   results = make_readable_bulk(pairs)
   
   # Update JSON with fixed colors
   for item, (fixed, status) in zip(data["colors"], results):
       item["fixed_text"] = fixed
       item["status"] = status

Filter by readability status
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from cm_colors import make_readable_bulk
   
   pairs = [("#777", "#fff"), ("#000", "#fff"), ("#ccc", "#fff")]
   results = make_readable_bulk(pairs)
   
   # Get only the readable ones
   readable = [(color, status) for color, status in results 
               if status in ["readable", "very readable"]]
   
   # Get ones that need attention
   not_readable = [(color, status) for color, status in results
                   if status == "not readable"]

See also
--------

* :doc:`how-to-fix-single-color-pair` - Fix one color
* :doc:`make-readable-bulk-api-reference` - Full API reference
* :doc:`troubleshooting-common-issues` - Solutions to problems
* :doc:`index` - Back to main page
