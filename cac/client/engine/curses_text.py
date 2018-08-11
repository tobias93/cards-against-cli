"""
This module helps with text rendering in curses.
"""
from enum import Enum
import curses


class TextAlignment(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2


class VerticalTextAlignment(Enum):
    TOP = 0
    CENTER = 1
    BOTTOM = 2


def render_text(
    win, text,
    x, y, w, h,
    word_wrap=False,
    fill_bg=False,
    alignment=TextAlignment.LEFT,
    valignment=VerticalTextAlignment.TOP,
    text_colour_pair=0,
    bg_colour_pair=None
):
    """
    Layouts and renders the given text.
    :param win: A curses window or pad object,
                where the text should be rendered to.
    :param x:
    :param y:
    :param w:
    :param h: x, y, w(idth) and h(eight) define a rectangular
                area that the text should be contained in.
    :param word_wrap:
                Should a line be continued in the next
                row, if it is longer than the width?
                If word_wrap is False, over-long lines will
                simply be cut of at the end.
    :param fill_bg:
                Defines, if and how the background should
                be filled.
                If fill_bg is False, the background will not be
                overwritten. Everything, that was rendered to the
                window before will act as background for the rendered text.
                If fill_bg is True, the background will be filled
                with spaces. This results in a clean background
                behind the text. Everything, that was previously
                rendered to the window in the given rectangular area
                will be overwritten.
                If fill_bg is a printable character, the background
                will be filled with this character instead of spaces.
    :param alignment:
                Alignment of the text.
                Lines, that are shorter than the given width will
                either be pushed to the left, to the right or centered
                based on this parameter.
    :param valignment:
                Vertical alignment of the text.
                Works like the alignment parameter, but for the vertical
                direction instead of the horizontal direction.
    :param text_colour_pair:
                The colour pair, that should be used to render the text.
                This can for example be obtained using the get_colour_pair_nr()
                method in the colour module.
    :param bg_colour_pair:
                The colour pair, that should be used to render te
                background. By default, the background is rendered using
                the same colour pair as the text.
    """

    # who on earth would try to show text with a with of 0...
    if w <= 0 or h <= 0:
        return

    # figure out the colours
    if bg_colour_pair is None:
        bg_colour_pair = text_colour_pair
    text_format = curses.color_pair(text_colour_pair)
    bg_format = curses.color_pair(bg_colour_pair)

    # make sure, no line is longer than w
    current_line = 0
    unprocessed_lines = text.split("\n")
    lines = []
    while current_line < len(unprocessed_lines):

        line = unprocessed_lines[current_line]

        if len(line) > w and word_wrap:
            last_space_pos = line.rfind(' ', 0, w + 1)
            if last_space_pos == -1:
                unprocessed_lines[current_line] = line[w:]
                line = line[:w]
                lines.append(line)
            elif last_space_pos == 0:
                unprocessed_lines[current_line] = line[1:]
            else:
                unprocessed_lines[current_line] = line[last_space_pos + 1:]
                line = line[:last_space_pos]
                lines.append(line)
        elif len(line) > w and not word_wrap:
            line = line[:w]
            lines.append(line)
            current_line += 1
        elif len(line) <= w:
            lines.append(line)
            current_line += 1

    # make sure, we do not have more lines than h
    if len(lines) > h:
        lines = lines[:h]

    # calculate the starting row
    if valignment == VerticalTextAlignment.TOP:
        y_start = 0
    elif valignment == VerticalTextAlignment.BOTTOM:
        y_start = h - len(lines)
    elif valignment == VerticalTextAlignment.CENTER:
        y_start = int((h - len(lines)) / 2)

    # which bg character to use
    clear_letter = ' '
    if isinstance(fill_bg, str) and len(fill_bg) == 1:
        clear_letter = fill_bg

    # draw
    for row, line in enumerate(lines, y + y_start):

        # calculate where to (horizontally) put the line
        if alignment == TextAlignment.LEFT:
            start_pos = 0
        elif alignment == TextAlignment.RIGHT:
            start_pos = w - len(line)
        elif alignment == TextAlignment.CENTER:
            start_pos = int((w - len(line)) / 2)

        # overwrite the part left and right of the line, if fill_bg is set.
        if fill_bg:

            # how much to clear
            clear_left = start_pos
            clear_right = w - start_pos - len(line)

            # clear
            if clear_left > 0:
                try:
                    win.addstr(
                        row, x,
                        clear_letter * clear_left,
                        bg_format)
                except curses.error:
                    # Attempting to write to the lower right corner of
                    # a window, subwindow, or pad will cause an exception
                    # to be raised after the character is printed.
                    # https://docs.python.org/3/library/curses.html#curses.window.addch
                    # AAARGH
                    # we'll hit the lower right corner quite often,
                    # so we just ignore this exception.
                    # (Also for the next calls of win.addstr - i will not
                    # repeat this comment every time.)
                    pass
            if clear_right > 0:
                try:
                    win.addstr(
                        row, x + w - clear_right,
                        clear_letter * clear_right,
                        bg_format)
                except curses.error:
                    pass

        # draw the line
        try:
            win.addstr(row, x + start_pos, line, text_format)
        except curses.error:
            pass

    # overwrite the part above and below the text block, if fill_bg is set.
    if fill_bg:

        # how much to clear
        clear_top = y_start
        clear_bottom = h - y_start - len(lines)

        # one full line of clear characters
        clear_line = clear_letter * w

        # clear
        for it in range(clear_top):
            try:
                win.addstr(y + it, x, clear_line, bg_format)
            except curses.error:
                pass
        for it in range(clear_bottom):
            try:
                win.addstr(y + h - it - 1, x, clear_line, bg_format)
            except curses.error:
                pass
