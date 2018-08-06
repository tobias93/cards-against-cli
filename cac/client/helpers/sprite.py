import curses
from cac.client.helpers.assets import get_asset_text_file
from cac.client.helpers.colour import get_colour_pair_nr


class Sprite:

    def __init__(self, asset_name):

        bad_file_exception = Exception("Malformed sprites file")
        pad = None
        width = 0
        height = 0
        next_row = 0
        colour_state = [(0, 0)]
        with get_asset_text_file(asset_name) as file:
            for line in file:

                line = line.rstrip("\n")

                # ignore empty lines
                if line == "":
                    continue

                # ignore comments
                if line[0] == '#':
                    continue

                # set the size of the sprite
                if line[0] == '+':
                    if pad is not None:
                        raise bad_file_exception
                    try:
                        size_list = [int(n) for n in line[1:].split(",")]
                    except ValueError:
                        raise bad_file_exception
                    if len(size_list) != 2:
                        raise bad_file_exception
                    width = size_list[0]
                    height = size_list[1]
                    pad = curses.newpad(height, width)
                    continue

                # color
                if line[0] == 'c':
                    colour_state = []
                    colour_items = line[1:].split(' ')
                    for colour_item_str in colour_items:
                        colour_item_parts_str = colour_item_str.split(',')
                        if len(colour_item_parts_str) != 7:
                            raise bad_file_exception
                        try:
                            pos = int(colour_item_parts_str[0])
                            fg_r = float(colour_item_parts_str[1])
                            fg_g = float(colour_item_parts_str[2])
                            fg_b = float(colour_item_parts_str[3])
                            bg_r = float(colour_item_parts_str[4])
                            bg_g = float(colour_item_parts_str[5])
                            bg_b = float(colour_item_parts_str[6])
                        except ValueError:
                            raise bad_file_exception
                        format_flag = curses.color_pair(get_colour_pair_nr(
                            fg_r, fg_g, fg_b, bg_r, bg_g, bg_b))
                        colour_state.append((pos, format_flag))
                    colour_state = sorted(colour_state)
                    if len(colour_state) == 0 or colour_state[0][0] != 0:
                        colour_state = [(0, 0)] + colour_state

                # read a row from the sprite
                if line[0] == ':':
                    text = line[1:]
                    if len(text) > width:
                        raise bad_file_exception
                    if len(text) < width:
                        text += " " * (width - len(text))
                    if next_row >= height:
                        raise bad_file_exception

                    curr_colourstate_pos = 0
                    while curr_colourstate_pos < len(colour_state):
                        cur_pos, cur_formatflag = colour_state[curr_colourstate_pos]
                        curr_colourstate_pos += 1
                        if curr_colourstate_pos >= len(colour_state):
                            next_pos = width
                        else:
                            next_pos, _ = colour_state[curr_colourstate_pos]
                        try:
                            pad.addstr(next_row, cur_pos, text[cur_pos:next_pos], cur_formatflag)
                        except curses.error:
                            pass
                    next_row += 1
        self._pad = pad
        self._width = width
        self._height = height

    def draw(self, win, x, y):
        h, w = win.getmaxyx()
        s_x, s_y = 0, 0
        d_x, d_y = x, y
        d_x2, d_y2 = x + self._width - 1, y + self._height - 1

        # clip on the border of the destination window
        if d_x < 0:
            s_x -= d_x
            d_x = 0
        if d_x >= w:
            return
        if d_x2 < 0:
            return
        if d_x2 >= w:
            d_x2 = w - 1
        if d_y < 0:
            s_y -= d_y
            d_y = 0
        if d_y >= h:
            return
        if d_y2 < 0:
            return
        if d_y2 >= h:
            d_y2 = h - 1

        # copy to the destination window
        self._pad.overwrite(win, s_y, s_x, d_y, d_x, d_y2, d_x2)

    @property
    def size(self):
        return self._width, self._height
