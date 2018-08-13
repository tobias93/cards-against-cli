"""
This module helps to manage the colours in curses.
"""
import curses
import math


init_done = False
colour_depth = None
colour_pair_cache = dict()
next_pair_nr = 1
next_pair_it = 0


def get_colour_pair(*args):
    """
    Returns a matching colour pair, that can be
    used within curses directly for text formatting.
    This function basically calls get_colour_pair_nr() for you and
    then passes the result into curses.color_pair() to get the
    actual text formatter.
    The function can be called either with 6 floats representing
    r/g/b values of the foreground and background colour
    or with two tuples, each containing 3 floats:

    get_colour_pair(fg, bg)
    get_colour_pair(fg_r, fg_g, fg_b, bg_r, bg_g, bg_b)

    The values r,g,b should be floating point numbers between 0 and 1.
    """

    # parse arguments - take either 2 tuples or 6 floats
    if len(args) == 6:
        fg = (args[0], args[1], args[2], )
        bg = (args[3], args[4], args[5], )
    elif len(args) == 2:
        fg = args[0]
        bg = args[1]
    else:
        raise TypeError(f"Wrong number of arguments.")

    # get colour
    colour_pair_nr = get_colour_pair_nr(*(fg + bg))
    return curses.color_pair(colour_pair_nr)


def get_colour_pair_nr(fg_r, fg_g, fg_b, bg_r, bg_g, bg_b):
    """
    Returns a matching colour pair number, that can be
    used with curses.color_pair() that closely resembles the given
    foreground and background r/g/b colours.
    The values r,g,b should be floating point numbers between 0 and 1.
    """

    global colour_pair_cache
    global next_pair_nr
    global next_pair_it

    # init
    init_palette()

    # fall back to white on black if the terminal is not fancy enough
    if not curses.has_colors() or not curses.can_change_color():
        return 0

    # get the fg colour
    fg = get_colour_nr(fg_r, fg_g, fg_b)
    bg = get_colour_nr(bg_r, bg_g, bg_b)

    # look up, if this colour pair is already configured
    key = fg, bg
    if key in colour_pair_cache:
        pair_nr, pair_it = colour_pair_cache[key]
        if pair_it == next_pair_it:
            return pair_nr

    # init the pair
    pair_nr = next_pair_nr
    pair_it = next_pair_it
    curses.init_pair(pair_nr, fg, bg)

    # store it in the colour pair cache
    colour_pair_cache[key] = pair_nr, pair_it

    # advance the pair_nr for the next colour pair
    next_pair_nr += 1
    if next_pair_nr >= 256:
        next_pair_nr = 1
        next_pair_it += 1

    # return result
    return pair_nr


def get_colour_nr(r, g, b):
    """
    Returns a matching colour number, that can be used within curses
    that closely resembles the given r/g/b colour.
    The values r,g,b should be floating point numbers between 0 and 1.
    """
    pr, pg, pb = get_closest_palette_colour(r, g, b)
    return get_palette_colour_number(pr, pg, pb)


def get_colour_depth():
    """
    Returns the maximum number of possible values per color channel,
    that can be used with the availible number of
    colours and colour pairs in the terminal.
    """
    nr_colours = curses.COLORS
    return int(math.pow(nr_colours, 1. / 3.))


def get_closest_palette_value(val):
    """
    Get the closest palette value for the given color depth.
    A palette value is an integer between 0 and colour_depth-1
    """
    pval = int(val * colour_depth)
    if pval == colour_depth:
        return colour_depth - 1
    else:
        return pval


def get_closest_palette_colour(r, g, b):
    """
    Utility function, that applies get_closest_palette_value to a
    r, g and b value.
    """
    return (
        get_closest_palette_value(r),
        get_closest_palette_value(g),
        get_closest_palette_value(b)
    )


def get_palette_colour_number(r, g, b):
    """
    Translates a colour in the palette space
    (as returned by get_closest_palette_colour)
    to a colour number that can be used for curses
    """
    return r + g * colour_depth + b * colour_depth * colour_depth


def init_palette():

    # just execute this once
    global init_done
    if init_done:
        return
    init_done = True

    # skip for terminals without colours
    if not curses.has_colors() or not curses.can_change_color():
        return

    # get the colour depth that we can archieve based
    # on the number of supported colours
    global colour_depth
    colour_depth = get_colour_depth()

    # init colours
    for r in range(colour_depth):
        for g in range(colour_depth):
            for b in range(colour_depth):
                colour_number = get_palette_colour_number(r, g, b)
                cursed_r = int(r / (colour_depth - 1) * 1000)
                cursed_g = int(g / (colour_depth - 1) * 1000)
                cursed_b = int(b / (colour_depth - 1) * 1000)
                curses.init_color(colour_number, cursed_r, cursed_g, cursed_b)
