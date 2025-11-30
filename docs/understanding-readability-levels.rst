Understanding Readability Levels
=================================

.. meta::
   :description: Learn what readable, very readable, and not readable mean for your colors. No jargon explanation of color readability standards.

What the readability levels mean.

The three levels
----------------

When you check colors, you get one of three results:

* **Very Readable**: Text stands out clearly. Easy for everyone to read.
* **Readable**: Text is clear enough. Most people can read it comfortably.
* **Not Readable**: Text is hard to read. Some people will struggle.

How to check
------------

.. code-block:: python

   from cm_colors import ColorPair

   pair = ColorPair("#777", "#fff")
   print(pair.is_readable)  # "Readable", "Very Readable", or "Not Readable"

When to use very readable
--------------------------

Use ``very_readable=True`` when:

* Text is important (legal text, instructions, body content)
* Users might have vision difficulties
* Text is small (under 18px)
* You want to be extra safe

.. code-block:: python

   from cm_colors import ColorPair

   pair = ColorPair("#888", "#fff")
   fixed, success = pair.make_readable(very_readable=True)

This aims for "Very Readable" instead of just "Readable".

Large text is more forgiving
-----------------------------

Large text (24px or bigger, or 19px+ if bold) is easier to read. It has less strict requirements.

Tell the library when you have large text:

.. code-block:: python

   from cm_colors import ColorPair

   # For headings, hero text, large buttons
   pair = ColorPair("#888", "#fff", large_text=True)
   fixed, success = pair.make_readable()

This might result in "Readable" where normal text would be "Not Readable".

Practical examples
------------------

Body text (small)
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from cm_colors import ColorPair

   # Body text should be very readable
   pair = ColorPair("#666", "#fff")
   fixed, success = pair.make_readable(very_readable=True)

Headlines (large)
~~~~~~~~~~~~~~~~~

.. code-block:: python

   from cm_colors import ColorPair

   # Headlines can use large_text flag
   pair = ColorPair("#888", "#fff", large_text=True)
   fixed, success = pair.make_readable()

Buttons
~~~~~~~

.. code-block:: python

   from cm_colors import ColorPair

   # Button text should be at least "Readable"
   pair = ColorPair("#999", "#3498db")
   fixed, success = pair.make_readable()

What affects readability
-------------------------

**Contrast**: How different the text and background are

* Black on white = Very Readable (maximum contrast)
* Dark gray on white = Readable  (good contrast)
* Light gray on white = Not Readable (low contrast)

**Size**: Larger text is easier to read

* 24px+ text can use lighter colors
* Small text needs darker colors

**Weight**: Bold text is easier to read

* 19px+ bold can use lighter colors
* Normal weight needs more contrast

Why this matters
----------------

Readable text means:

* More people can use your app/site
* Users don't strain their eyes
* Text is clear in different lighting
* Meets basic usability standards

When "not readable" is OK
--------------------------

Sometimes you get "not readable" even after fixing. This happens when:

* Original color is very light (like ``#eee``)
* Making it readable would change it too much
* You're using strict mode (``mode=0``)

If you need it readable:

1. Try relaxed mode: ``make_readable(mode=2)``
2. Use very_readable: ``make_readable(very_readable=True)`` 
3. Manually pick a darker color

Quick reference
---------------

==================== =============== =====================
Status               What it means   When to use
==================== =============== =====================
Very Readable        Excellent       Body text, important content
Readable             Good enough     Most text
Not Readable         Needs work      Avoid for text
==================== =============== =====================

Technical note (optional)
-------------------------

These levels map to WCAG standards:

* "Very Readable" = AAA level
* "Readable" = AA level  
* "Not Readable" = Fails AA

You don't need to know this to use the library. The simple labels ("Readable") tell you everything you need.

See also
--------

* :doc:`how-to-fix-single-color-pair` - Fix colors based on readability
* :doc:`troubleshooting-common-issues` - When colors won't fix
* :doc:`colorpair-api-reference` - Full API reference
* :doc:`index` - Back to main page
