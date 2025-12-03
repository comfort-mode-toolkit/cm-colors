Readability Standards & CM-Colors
===================================

.. meta::
   :description: How CM-Colors terms map to WCAG standards. Understand what "Readable" and "Very Readable" mean for your compliance requirements.

This guide explains how our simple terms map to official accessibility standards (WCAG). Use this if you need to verify compliance for a ticket or audit.

Mapping Terms to Standards
--------------------------

We use simple language, but it maps directly to strict mathematical standards.

.. list-table::
   :widths: 20 20 60
   :header-rows: 1

   * - CM-Colors Output
     - WCAG Level
     - What it means
   * - **"Readable"**
     - **AA**
     - The global standard. Required for most government and business websites.
   * - **"Very Readable"**
     - **AAA**
     - The strict standard. For enhanced accessibility or critical text.
   * - **"Not Readable"**
     - **Fail**
     - Does not meet minimum contrast requirements.

How to check compliance
-----------------------

You can check the exact status of any color pair in Python:

.. code-block:: python

   from cm_colors import ColorPair

   pair = ColorPair("#767676", "#ffffff")
   
   print(pair.is_readable)
   # Output: "Readable"  <-- This means it passes WCAG AA

   # If you need AAA (Very Readable):
   if pair.is_readable != "Very Readable":
       print("Does not meet AAA standard")

Meeting Specific Goals
----------------------

Goal: "I need to pass WCAG AA"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the default settings. `make_readable()` aims for AA by default because it's the industry standard.

.. code-block:: python

   # Fixes color to meet WCAG AA (4.5:1 ratio)
   fixed, success = pair.make_readable()

Goal: "I need to pass WCAG AAA"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Use the `very_readable` flag. This tells the tool to target the 7:1 contrast ratio required for AAA.

.. code-block:: python

   # Fixes color to meet WCAG AAA (7:1 ratio)
   fixed, success = pair.make_readable(very_readable=True)

Goal: "I have large text (headings)"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

WCAG has looser rules for large text (18pt+ or 14pt+ bold). Tell us about it so we don't darken your colors unnecessarily.

.. code-block:: python

   # Uses the large text standard (3:1 for AA)
   pair = ColorPair("#999", "#fff", large_text=True)
   fixed, success = pair.make_readable()

Summary Table
-------------

| Your Goal | CM-Colors Setting | Target Contrast Ratio |
| :--- | :--- | :--- |
| **Standard Text (AA)** | `make_readable()` | 4.5:1 |
| **Large Text (AA)** | `make_readable(large_text=True)` | 3:1 |
| **Standard Text (AAA)** | `make_readable(very_readable=True)` | 7:1 |
| **Large Text (AAA)** | `make_readable(very_readable=True, large_text=True)` | 4.5:1 |

You don't need to memorize the ratios. Just know that **Readable = AA** and **Very Readable = AAA**.
