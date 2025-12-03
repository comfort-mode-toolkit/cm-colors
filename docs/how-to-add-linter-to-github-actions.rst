How to Add Linter to GitHub Actions
=====================================

.. meta::
   :description: Automatically check color contrast on every Pull Request. Integrate Color Contrast Linter into your GitHub Actions CI/CD pipeline.

Ensure your app stays accessible by checking colors automatically on every code change.

The goal
--------

We want to run the **Color Contrast Linter** every time someone pushes code or opens a Pull Request. If they add a color that isn't readable, the build will fail, preventing the bad color from merging.

Step 1: Create the workflow file
--------------------------------

Create a new file in your repository at:
``.github/workflows/color-contrast.yml``

Step 2: Add the configuration
-----------------------------

Paste this code into the file:

.. code-block:: yaml

   # .github/workflows/color-contrast.yml
   name: Color Contrast Check
   on:
   push:
      branches: [ main ]
   pull_request:
      branches: [ main ]

   jobs:
     lint-colors:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         
         - name: Check Color Contrast
           uses: comfort-mode-toolkit/color-contrast-linter-action@main

Step 3: Add your color config
-----------------------------

Make sure you have a ``.color_pairs.yml`` file in the root of your repository.

If you don't have one, run this locally to create it:

.. code-block:: bash

   pip install color-contrast-linter
   cc-lint init

Then commit and push this file.

How it works
------------

1. You push code to GitHub.
2. GitHub Actions sees the ``accessibility.yml`` file and starts a job.
3. It installs the linter and reads your ``.color_pairs.yml``.
4. It checks all your defined color pairs.
5. **If all pass**: You get a green checkmark 
6. **If any fail**: You get a red X and the build fails.

Viewing results
---------------

Click on the "Actions" tab in your GitHub repository to see the results. You'll see a detailed log showing exactly which colors passed and failed.

Blocking bad merges
-------------------

To strictly enforce accessibility:

1. Go to your repository **Settings**.
2. Click **Branches** → **Branch protection rules**.
3. Edit your main branch rule.
4. Check **Require status checks to pass before merging**.
5. Select **lint-colors** from the list.

Now, nobody can merge code that breaks your color accessibility rules!

See also
--------

* :doc:`how-to-use-color-contrast-linter` - Learn how to configure the linter
* :doc:`what-makes-cm-colors-work` - Understand why we care about contrast
