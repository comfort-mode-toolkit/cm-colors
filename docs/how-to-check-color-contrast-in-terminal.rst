Check Color Contrast in the Terminal
======================================

.. meta::
   :description: Check WCAG color contrast ratios from the terminal. Single pair and bulk checking with JSON output — built for AI agents, CI/CD pipelines, and shell scripts. No browser required.
   :keywords: check color contrast terminal, wcag contrast ratio cli, color contrast command line, color contrast checker for agents, wcag contrast ratio json

Get a WCAG contrast ratio for any two colors — from any shell, script, or AI agent.

.. code-block:: bash

   cm-colors contrast '#777777' '#ffffff'

Output:

.. code-block:: text

   ┌──────────┬──────────┬─────────┬───────┬───┐
   │ FG       │ BG       │   Ratio │ Level │   │
   ├──────────┼──────────┼─────────┼───────┼───┤
   │ #777777  │ #ffffff  │  4.48:1 │  AA   │ ✓ │
   └──────────┴──────────┴─────────┴───────┴───┘

Installation
------------

.. code-block:: bash

   pip install cm-colors

Single pair
-----------

Pass foreground and background as positional arguments.
Accepts any format cm-colors understands: hex, RGB, named colors.

.. code-block:: bash

   # Hex
   cm-colors contrast '#777777' '#ffffff'

   # Named colors
   cm-colors contrast 'gray' 'white'

   # RGB strings
   cm-colors contrast 'rgb(119,119,119)' 'rgb(255,255,255)'

Add ``--large`` when checking headings or text over 24 px (WCAG large-text thresholds apply):

.. code-block:: bash

   cm-colors contrast '#888888' '#ffffff' --large

JSON output for agents and scripts
-----------------------------------

Add ``--json`` to get machine-readable output on stdout.
This is the recommended interface for AI agents and CI scripts.

.. code-block:: bash

   cm-colors contrast '#777777' '#ffffff' --json

.. code-block:: json

   {
     "fg": "#777777",
     "bg": "#ffffff",
     "ratio": 4.48,
     "level": "AA",
     "pass": true,
     "large": false
   }

Fields:

* **fg** / **bg** — colors normalized to hex
* **ratio** — WCAG contrast ratio (rounded to 2 decimal places)
* **level** — ``"AAA"``, ``"AA"``, or ``"FAIL"``
* **pass** — ``true`` when level is AA or AAA, ``false`` when FAIL
* **large** — reflects the ``--large`` flag

Exit codes
----------

The command exits ``0`` when all pairs pass and ``1`` when any pair fails.
Use this in shell conditionals and CI gates:

.. code-block:: bash

   if cm-colors contrast '#777777' '#ffffff' --json > /dev/null; then
       echo "Contrast passes"
   else
       echo "Contrast fails — fix the color"
   fi

Bulk checking from a file
--------------------------

Put pairs in a plain text file, one ``FG BG`` per line.
Lines starting with ``#`` are treated as comments.

.. code-block:: text

   # brand-colors.txt
   #3d3d3d #ffffff
   #777777 #ffffff
   #aaaaaa #000000

.. code-block:: bash

   cm-colors contrast --file brand-colors.txt

Bulk JSON output includes a summary:

.. code-block:: bash

   cm-colors contrast --file brand-colors.txt --json

.. code-block:: json

   {
     "results": [
       {"fg": "#3d3d3d", "bg": "#ffffff", "ratio": 9.73, "level": "AAA", "pass": true, "large": false},
       {"fg": "#777777", "bg": "#ffffff", "ratio": 4.48, "level": "AA",  "pass": true, "large": false},
       {"fg": "#aaaaaa", "bg": "#000000", "ratio": 4.60, "level": "AA",  "pass": true, "large": false}
     ],
     "summary": {
       "total": 3,
       "pass": 3,
       "fail": 0
     }
   }

Using from an AI agent
-----------------------

Any agent that can run shell commands can call ``cm-colors contrast`` and parse the JSON response.

Typical pattern:

1. Run ``cm-colors contrast FG BG --json``
2. Parse the JSON
3. Read ``pass`` to decide whether the colors are accessible
4. If ``pass`` is ``false``, call ``cm-colors fix`` or the Python API to get a fixed color

Example tool call an agent might make:

.. code-block:: bash

   cm-colors contrast '#aaaaaa' '#f5f5f5' --json

.. code-block:: json

   {
     "fg": "#aaaaaa",
     "bg": "#f5f5f5",
     "ratio": 2.32,
     "level": "FAIL",
     "pass": false,
     "large": false
   }

The agent sees ``"pass": false`` and knows to request a fix.

WCAG levels explained
---------------------

* **AAA** — ratio ≥ 7.0 (normal text) or ≥ 4.5 (large text). Highest standard.
* **AA** — ratio ≥ 4.5 (normal text) or ≥ 3.0 (large text). Legal minimum for most accessibility requirements.
* **FAIL** — ratio below the AA threshold. Text will be hard to read for many users.

See also
--------

* :doc:`how-to-fix-single-color-pair` — Fix a failing pair with one function call
* :doc:`how-to-fix-multiple-colors-bulk` — Fix many colors at once
* :doc:`how-to-use-color-contrast-linter` — Lint CSS files for contrast issues
* :doc:`accessibility-explained` — How WCAG contrast maps to "readable"
