from cm_colors.core.conversions import (
    rgb_to_oklch_safe,
    oklch_to_rgb_safe,
    is_valid_rgb,
    parse_color_to_rgb,
    rgbint_to_string,
)

from cm_colors.core.contrast import calculate_contrast_ratio, get_wcag_level

from collections import state #ik this is not the right import but i forgot the right name so, fix this

from optimisation import check_and_fix_contrast

    
class Color:
    def __init__(self,color,type=None,background_context=None):
        self.original_color = color
        self.color = None
        self.type=type
        self.background_context = None

        @state
        def color(self):
            # if background context is given, aka the bg color ( of Color class ), use it to blend for rgba to rgb
            # parse function that handles rgba ( from pr #11 ), rgb, hex, namedcolor in string / css string / tuple / list
            pass

        def to_hex(self):
            # returns string of format '#______' - css style
            pass
        
        def to_rgb(self):
            # returns string of format 'rgb(xx,xx,xx)' - css style
            return f'rgb({self.color[0]},{self.color[1]},{self.color[2]})'

        def to_oklch(self):
            # returns string of format 'oklch(??)' - css style
            pass


class ColorPair:
    def __init__(self,text_color,bg_color,large_text=False):
        self.bg = Color(bg_color,'bg')
        self.text = Color(text_color,'text',background_context=self.bg)
        self.large_text = large_text
        self.contrast = None
        self.a11y = None

    @state
    def contrast(self):
        return calculate_contrast_ratio(self.bg.color,self.text.color)
    
    @state
    def a11y(self):
        return get_wcag_level(self.bg.color,self.text.color,self.large_text)

    
"""final main func format would be like
def tune_color(text_color,bg_color,large_text=False,details=False):
    color_pair = ColorPair(text_color,bg_color,large_text)
    tuned_text,is_accessible = check_and_fix_contrast(ColorPair,details=details)

    if is_accessible:
        # return the tuned_text,bg ColorPair
    else:
        notify it's not accessible even with tuning, please pick better starting color or smth like this ( return value not yet fixed !! Choose the best )

    # main point is to make sure it is both usable for single ColorPair like manual library usage but also for bulk through a cli
    so that it isn't a mess or huge list of this accessible this not, we need to be as minimal as 'black .'

    We need to break down so that errors are caught well so is feedback 
    1. Parse the colors to rgb and store, else throw error
    2. Tune colors
    3. return is_accessible, tuned_text

    we need to ensure that if we were to bulk call this tune_color() func, it's easily readable through a cli too without the code breaking at single error

    rather cli would somehow should be able to handle this like:

    hello I am color cheetah, tuning your colors to make it more readable ( if not already )
    x color pairs found
    great job x-y pairs are accessible already
    tuning the y pairs to see if we can make it accessible.....
    y-z pairs are now accessible after tuning!!
    unfortunately, tunign didnt fix contrast for z pairs, here are those
    ... text_color,bg_color ( found under .blabla css class )
    please try picking better starting colors
    x found, x-a pairs are now accessible, please pick better starting colors for a pairs 
    Great job!!



"""
