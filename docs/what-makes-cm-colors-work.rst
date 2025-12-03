What Makes CM-Colors Work
===========================

.. meta::
   :description: How CM-Colors fixes readability without ruining your design. A look at the smart color science behind the tool, explained simply.

Most color tools just darken colors until they pass a test. This ruins your design.

We took a different approach. We wanted to fix readability while keeping the "soul" of your colors.

The problem with "just darken it"
---------------------------------

If you have a light blue that's hard to read, the standard fix is to make it darker blue.

But "darker" often means "muddy" or "dull". A vibrant sky blue becomes a boring navy. Your friendly app starts looking like a corporate spreadsheet.

We realized that readability isn't just about lightness. It's about how our eyes perceive color.

How we see color
----------------

Computers see color as Red, Green, and Blue (RGB). Humans don't.

We see:
1. **Lightness**: How bright it is
2. **Chroma**: How colorful or vivid it is
3. **Hue**: What "color" it is (red, blue, green)

Standard tools mess with all three. They might darken your blue (Lightness) but also accidentally make it purple (Hue) or gray (Chroma).

Our approach: The Scalpel, not the Hammer
-----------------------------------------

CM-Colors uses a modern color space called **OKLCH**. It's designed to model how human eyes actually work.

This allows us to be surgical:

1. **Lock the Hue**: We never change *what* color it is. Blue stays blue. Red stays red.
2. **Preserve the Chroma**: We try hard to keep the vividness. If you chose a bright color, we keep it bright.
3. **Adjust only Lightness**: We carefully tune *just* the lightness until text becomes readable.

The "Smart Search"
------------------

Finding the perfect color is a game of "Hot or Cold".

1. We start with your original color.
2. We ask: "Is this readable?"
3. If no, we make a tiny adjustment to lightness.
4. We check again.
5. We repeat this dozens of times in a fraction of a second.

But here's the secret sauce: **We don't just stop at "readable".**

Once we find a readable color, we check: "Is this too different from the original?"

If it is, we try a different trick: we trade a tiny bit of vividness (Chroma) to get better readability without changing the lightness as much. This often preserves the "feel" of the color better than just darkening it.

The result
----------

* **Before**: A light blue that's hard to read.
* **Standard Tool**: A dark, dull navy blue.
* **CM-Colors**: A rich, readable blue that still feels like your brand.

We do the complex math so you don't have to. You just get colors that work.