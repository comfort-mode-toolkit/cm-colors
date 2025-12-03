Use Without Programming
=======================

.. meta::
   :description: How to use CM-Colors without writing any code. Use Google Colab to fix colors in your browser.

You don't need to be a programmer to use CM-Colors. We have a ready-to-use notebook that runs in your browser.

Step 1: Open Google Colab
-------------------------

Click this link to open a new notebook: `Google Colab <https://colab.research.google.com/>`_

Step 2: Install CM-Colors
-------------------------

In the first cell, type this and press the Play button (▶️):

.. code-block:: bash

   !pip install cm-colors

Step 3: Fix your colors
-----------------------

Copy and paste this code into a new cell:

.. code-block:: python

   from cm_colors import make_readable_bulk

   # Paste your colors here
   my_colors = [
       ("#777", "#fff"),
       ("#888", "#000"),
       ("red", "white"),
   ]

   # Fix them
   results = make_readable_bulk(my_colors, save_report=True)

   # Print results
   for color, status in results:
       print(f"{color} - {status}")

Press Play. You will see the fixed colors printed below.

Step 4: See the report
----------------------

On the left sidebar, click the folder icon 📁. You will see a file named ``cm_colors_bulk_report.html``.

Right-click it and select **Download**. Open it in your browser to see a visual report of all changes.

Common Tasks
------------

Fix a spreadsheet
~~~~~~~~~~~~~~~~~

1. Export your spreadsheet to CSV.
2. Upload it to Colab (folder icon -> upload).
3. Use Python to read it:

.. code-block:: python

   import pandas as pd
   from cm_colors import make_readable_bulk

   # Read file
   df = pd.read_csv("colors.csv")

   # Create pairs list (assuming columns 'Text' and 'Background')
   pairs = list(zip(df['Text'], df['Background']))

   # Fix colors
   results = make_readable_bulk(pairs)

   # Add results back to spreadsheet
   df['Fixed Text'] = [r[0] for r in results]
   df['Status'] = [r[1] for r in results]

   # Save
   df.to_csv("colors_fixed.csv", index=False)

4. Download ``colors_fixed.csv``.
