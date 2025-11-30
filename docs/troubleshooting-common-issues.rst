Troubleshooting Common Issues
==============================

.. meta::
   :description: Solutions to common problems when fixing color contrast with CM-Colors. Learn how to handle colors that won't fix, preserve brand colors, and more.

Solutions to problems you might run into.

Colors still not readable
-------------------------

**Problem**: Called ``make_readable()`` but colors still hard to read.

**Solution**: Use ``very_readable=True``:

.. code-block:: python

   from cm_colors import ColorPair

   pair = ColorPair("#aaa", "#fff")
   fixed, success = pair.make_readable(very_readable=True)

This aims for stricter readability standards.

Colors changed too much
-----------------------

**Problem**: Fixed color looks too different from original.

**Solution**: Use strict mode (``mode=0``):

.. code-block:: python

   from cm_colors import ColorPair

   pair = ColorPair("#888", "#fff")
   fixed, success = pair.make_readable(mode=0)

This minimizes color changes but might not fix all colors.

Function returns "not readable"
-------------------------------

**Problem**: Status says "not readable" even after fixing.

**What it means**: The color is as close to readable as possible while staying similar to the original.

**Solutions**:

1. Use relaxed mode:

   .. code-block:: python

      fixed, success = pair.make_readable(mode=2)

2. Use very_readable flag:

   .. code-block:: python

      fixed, success = pair.make_readable(very_readable=True)

3. Manually pick a different color that's further from the original

Need to preserve exact brand colors
------------------------------------

**Problem**: Brand guidelines require exact colors, but they're not readable.

**Solution**: This library always changes colors slightly to make them readable. If you must keep exact colors, you'll need to:

1. Get approval to adjust brand colors for readability
2. Use strict mode (``mode=0``) for minimal changes
3. Update brand guidelines with the fixed colors

Large text not detected
-----------------------

**Problem**: Have large text but colors not adjusting correctly.

**Solution**: Explicitly set ``large_text=True``:

.. code-block:: python

   from cm_colors import ColorPair

   # For headings, hero text, large buttons
   pair = ColorPair("#888", "#fff", large_text=True)
   fixed, success = pair.make_readable()

Large text has more lenient readability requirements.

Format not preserved
--------------------

**Problem**: Input hex code, got RGB tuple back.

**This shouldn't happen**. If it does:

1. Make sure you're using the latest version: ``pip install --upgrade cm-colors``
2. Check that your input is a string: ``"#777"`` not a number
3. Report as a bug if issue persists

Correct behavior:

.. code-block:: python

   from cm_colors import ColorPair

   # Hex in, hex out
   pair = ColorPair("#777", "#fff")
   fixed, success = pair.make_readable()
   # fixed is "#757575" (string)

   # Tuple in, tuple out
   pair = ColorPair((119, 119, 119), (255, 255, 255))
   fixed, success = pair.make_readable()
   # fixed is (117, 117, 117) (tuple)

Processing takes too long
--------------------------

**Problem**: Bulk processing is slow.

**Solutions**:

1. Use default mode (``mode=1``) which is fastest
2. Process in smaller batches if you have thousands of colors
3. Don't use ``very_readable=True`` unless needed (it's slower)

Example for large datasets:

.. code-block:: python

   from cm_colors import make_readable_bulk

   # Process in batches of 100
   all_pairs = [...]  # Your thousands of pairs
   batch_size = 100

   all_results = []
   for i in range(0, len(all_pairs), batch_size):
       batch = all_pairs[i:i + batch_size]
       results = make_readable_bulk(batch)
       all_results.extend(results)

Want to see what changed
-------------------------

**Problem**: Need to review all color changes.

**Solution**: Use ``save_report=True``:

.. code-block:: python

   from cm_colors import ColorPair

   pair = ColorPair("#777", "#fff")
   fixed, success = pair.make_readable(save_report=True)
   # Creates cm_colors_quick_report.html

   # Or for bulk
   from cm_colors import make_readable_bulk

   results = make_readable_bulk(pairs, save_report=True)
   # Creates cm_colors_bulk_report.html

Open the HTML file in your browser to see before/after visual comparison.

Colors look different in browser
---------------------------------

**Problem**: Fixed colors look different when actually used.

**Common causes**:

1. **Display settings**: Check your monitor's color profile and brightness
2. **Browser rendering**: Different browsers can show colors slightly differently
3. **Lighting conditions**: Color perception changes with ambient lighting

The library uses industry-standard color calculations. If colors are readable in the report, they're readable.

Invalid color errors
--------------------

**Problem**: Getting "invalid color" errors or status.

**Solutions**:

1. Check color format is correct:

   .. code-block:: python

      # Correct
      ColorPair("#777777", "#ffffff")  # 6-digit hex
      ColorPair((119, 119, 119), (255, 255, 255))  # RGB 0-255

      # Wrong
      ColorPair("#777", "#fff")  # 3-digit works but 6 is clearer
      ColorPair((1.0, 0.5, 0.5), (1.0, 1.0, 1.0))  # Use 0-255, not 0-1

2. Check for typos in CSS color names

3. Use ``pair.is_valid`` to check before processing:

   .. code-block:: python

      pair = ColorPair(text, bg)
      if pair.is_valid:
          fixed, success = pair.make_readable()
      else:
          print(f"Invalid colors: {pair.errors}")

CSS variables not updating
---------------------------

**Problem**: Fixed CSS file but variables still show old colors.

**Solution**: The CLI tool updates variable definitions. Make sure you're looking at the ``_cm.css`` file, not the original.

The tool changes this:

.. code-block:: css

   /* Original */
   :root {
     --text-color: #999;
   }

To this:

.. code-block:: css

   /* Fixed */
   :root {
     --text-color: #8e8e8e;  /* Made readable */
   }

All usages of ``var(--text-color)`` will automatically use the new value.

Still having problems?
----------------------

If none of these solutions help:

1. Check you're using the latest version: ``pip install --upgrade cm-colors``
2. Try the example code from :doc:`how-to-fix-single-color-pair` to verify installation
3. Check that your Python version is 3.8 or newer

See also
--------

* :doc:`how-to-fix-single-color-pair` - Basic usage guide
* :doc:`colorpair-api-reference` - Full API documentation
* :doc:`understanding-readability-levels` - What readability means
* :doc:`index` - Back to main page
