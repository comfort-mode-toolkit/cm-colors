Check Color Contrast in the Terminal
======================================

.. meta::
   :description: Check and fix WCAG color contrast ratios from the terminal. Single pair and bulk checking with JSON output — built for AI agents, CI/CD pipelines, and shell scripts. No browser required.
   :keywords: check color contrast terminal, wcag contrast ratio cli, color contrast command line, color contrast checker for agents, wcag contrast ratio json, fix color contrast terminal

Check or fix contrast for any two colors from any shell, script, or AI agent.

.. code-block:: bash

   cm-colors contrast '#777777' '#ffffff' --json
   cm-colors fix     '#777777' '#ffffff' --json

Both commands use the same syntax for single pairs, inline bulk, and file bulk.

Installation
------------

.. code-block:: bash

   pip install cm-colors

Command overview
----------------

``contrast`` — read-only check. Returns ratio, level, pass/fail. Never modifies colors.

``fix`` — returns a fixed color that passes WCAG. Accepts the same inputs as ``contrast``
and also works on CSS files.

Single pair
-----------

Pass foreground and background as positional arguments.
Accepts any format: hex, ``rgb()``, ``hsl()``, or CSS named colors.

.. code-block:: bash

   cm-colors contrast '#777777' '#ffffff'
   cm-colors fix     '#777777' '#ffffff'

   # Named colors
   cm-colors contrast 'gray' 'white'

   # RGB strings
   cm-colors fix 'rgb(119,119,119)' 'rgb(255,255,255)'

   # Large text thresholds (AA >= 3.0, AAA >= 4.5)
   cm-colors contrast '#888888' '#ffffff' --large
   cm-colors fix     '#888888' '#ffffff' --large

Inline bulk — no file needed
------------------------------

Pass ``--pairs "FG BG"`` once per pair. Works on both commands.
This is the recommended form when an agent is building the list dynamically.

.. code-block:: bash

   cm-colors contrast --pairs '#777 #fff' --pairs '#aaa #000' --json

   cm-colors fix --pairs '#777 #fff' --pairs '#aaa #000' --json

Bulk from file
--------------

One ``FG BG`` pair per line. Lines starting with ``# `` are comments.
Hex colors starting with ``#`` are not treated as comments.

.. code-block:: text

   # brand-colors.txt
   #3d3d3d #ffffff
   #777777 #ffffff
   #aaaaaa #000000

.. code-block:: bash

   cm-colors contrast --file brand-colors.txt --json
   cm-colors fix     --file brand-colors.txt --json

JSON output
-----------

Add ``--json`` to get machine-readable output. Without it, output is a table for humans.

**contrast — single pair:**

.. code-block:: bash

   cm-colors contrast '#777777' '#ffffff' --json

.. code-block:: json

   {
     "fg": "#777777",
     "bg": "#ffffff",
     "ratio": 4.48,
     "level": "FAIL",
     "pass": false,
     "large": false
   }

**fix — single pair:**

.. code-block:: bash

   cm-colors fix '#777777' '#ffffff' --json

.. code-block:: json

   {
     "fg": "#777777",
     "bg": "#ffffff",
     "fixed": "#757575",
     "ratio": 4.61,
     "level": "AA",
     "success": true
   }

**Bulk adds a summary object:**

.. code-block:: json

   {
     "results": [ ... ],
     "summary": { "total": 3, "pass": 3, "fail": 0 }
   }

JSON fields for ``contrast``: ``fg``, ``bg``, ``ratio``, ``level``, ``pass``, ``large``

JSON fields for ``fix``: ``fg``, ``bg``, ``fixed``, ``ratio``, ``level``, ``success``

Exit codes
----------

Both commands exit ``0`` when all pairs pass/succeed, ``1`` when any fail.

.. code-block:: bash

   if cm-colors contrast '#777777' '#ffffff' --json > /dev/null; then
       echo "passes"
   else
       cm-colors fix '#777777' '#ffffff' --json
   fi

Very readable (AAA)
-------------------

By default ``fix`` targets WCAG AA (ratio 4.5). Add ``--very-readable`` to target AAA (ratio 7.0).
This mirrors the ``very_readable=True`` parameter in the Python API.

.. code-block:: bash

   cm-colors fix '#777777' '#ffffff' --very-readable --json

.. code-block:: json

   {
     "fg": "#777777",
     "bg": "#ffffff",
     "fixed": "#595959",
     "ratio": 7.0,
     "level": "AAA",
     "success": true
   }

Fix CSS files
-------------

``fix`` also works on CSS files and directories (the original behavior):

.. code-block:: bash

   cm-colors fix ./styles/
   cm-colors fix ./styles/ --very-readable
   cm-colors fix ./styles/ --mode 0    # Strict: minimize color change

Using from an AI agent
-----------------------

Typical agent workflow:

1. ``cm-colors contrast FG BG --json`` — check
2. Read ``"pass"`` — if ``false``, proceed
3. ``cm-colors fix FG BG --json`` — get fixed color
4. Read ``"fixed"`` — use that value

For many pairs at once, use ``--pairs`` so the agent does not need to write a temp file:

.. code-block:: bash

   cm-colors fix --pairs '#777 #fff' --pairs '#aaa #f5f5f5' --json

WCAG levels
-----------

* **AAA** — ratio >= 7.0 (normal) or >= 4.5 (large). Highest standard.
* **AA** — ratio >= 4.5 (normal) or >= 3.0 (large). Required for most accessibility compliance.
* **FAIL** — below AA. Hard to read for many users.

See also
--------

* :doc:`how-to-fix-single-color-pair` — Fix a pair from Python
* :doc:`how-to-fix-multiple-colors-bulk` — Fix many colors with the Python API
* :doc:`how-to-use-color-contrast-linter` — Lint CSS files for contrast issues
* :doc:`accessibility-explained` — How WCAG levels map to "readable"
