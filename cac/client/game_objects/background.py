import numpy as np
import random
import math
import curses
from typing import Optional

from cac.client.engine.game_object import GameObject
from cac.client.engine.curses_colour import get_colour_pair

random.seed()


def get_random_wave_parameters():
    angle = random.random() * math.pi * 2
    wavelenght = 8 + random.random() * 100
    amplitude = .5 + .5 + random.random()
    phase = random.random() * 2 * math.pi
    return angle, wavelenght, amplitude, phase


def eval_wave(w, h, angle, wavelenght, amplitude, phase):
    dy = math.sin(angle)
    dx = math.cos(angle)
    center_x = w / 2
    center_y = h / 2
    frequency = 1 / wavelenght
    data = np.zeros((w, h))
    for x in range(w):
        for y in range(h):
            t = (x-center_x) * dx + (y-center_y) * dy
            data[x, y] = math.sin(t * frequency * 2 * math.pi + phase) * \
                amplitude
    return data


def interpolate_wave_parameters(t, angle_1, wavelenght_1, amplitude_1, phase_1,
                                angle_2, wavelenght_2, amplitude_2, phase_2):

    # find out, if going clockwise or counterclockwise is faster...
    while angle_2 >= angle_1:
        angle_2 -= math.pi
        phase_2 = math.pi - phase_2
    while angle_2 < angle_1:
        angle_2 += math.pi
        phase_2 = math.pi - phase_2
    if angle_2 - angle_1 > (angle_1 - angle_2 + math.pi):
        angle_2 = angle_2 - math.pi
        phase_2 = math.pi - phase_2

    # the same thing for the phase
    while phase_2 >= phase_1:
        phase_2 -= 2 * math.pi
    while phase_2 < phase_1:
        phase_2 += 2 * math.pi
    if phase_2 - phase_1 > phase_1 - phase_2 + 2 * math.pi:
        phase_2 -= 2 * math.pi
    t_ = 1 - t
    return angle_1 * t_ + angle_2 * t, \
        wavelenght_1 * t_ + wavelenght_2 * t, \
        amplitude_1 * t_ + amplitude_2 * t, \
        phase_1 * t_ + phase_2 * t


def wave_diff(wa, wb):
    wb = interpolate_wave_parameters(1, *wa, *wb)
    return abs(wa[0] - wb[0])


def match_wave_parameters(wa1, wa2, wa3, wb1, wb2, wb3):
    diff_11 = wave_diff(wa1, wb1)
    diff_12 = wave_diff(wa1, wb2)
    diff_13 = wave_diff(wa1, wb3)
    diff_21 = wave_diff(wa2, wb1)
    diff_22 = wave_diff(wa2, wb2)
    diff_23 = wave_diff(wa2, wb3)
    diff_31 = wave_diff(wa3, wb1)
    diff_32 = wave_diff(wa3, wb2)
    diff_33 = wave_diff(wa3, wb3)
    score_123 = diff_11 + diff_22 + diff_33
    score_132 = diff_11 + diff_23 + diff_32
    score_213 = diff_12 + diff_21 + diff_33
    score_231 = diff_12 + diff_23 + diff_31
    score_312 = diff_13 + diff_21 + diff_32
    score_321 = diff_13 + diff_22 + diff_31
    best_score = min([score_123, score_132, score_213,
                      score_231, score_312, score_321])
    if score_123 == best_score:
        return wa1, wb1, wa2, wb2, wa3, wb3
    if score_132 == best_score:
        return wa1, wb1, wa2, wb3, wa3, wb2
    if score_213 == best_score:
        return wa1, wb2, wa2, wb1, wa3, wb3
    if score_231 == best_score:
        return wa1, wb2, wa2, wb3, wa3, wb1
    if score_312 == best_score:
        return wa1, wb3, wa2, wb1, wa3, wb2
    if score_321 == best_score:
        return wa1, wb3, wa2, wb2, wa3, wb1


class HypnoBackground(GameObject):

    def __init__(self, transition_from: Optional['HypnoBackground'] = None):

        super().__init__()

        self.last_bg_pattern = np.zeros((0, 0))

        self.wave_parameters = tuple(get_random_wave_parameters()
                                     for i
                                     in range(3))

        self.style1_character = '.'
        self.style1_colour_fg = (0, 1, 1)
        self.style1_colour_bg = (0, 1, 1)

        self.style2_character = '.'
        self.style2_colour_fg = (0, 0, 0)
        self.style2_colour_bg = (1, 0, 0)

        self.border_character = ' '
        self.border_colour_fg = (0, 0, 0)
        self.border_colour_bg = (0, 0, 0)

        self.transition_from = transition_from
        self.transition_pos = 1.0 if transition_from is None else 0.0
        self.transition_speed = 1

        # make the transition animation match nicely
        if transition_from is not None:
            wa1, wb1, wa2, wb2, wa3, wb3 = match_wave_parameters(
                *self.wave_parameters,
                *transition_from.wave_parameters)
            self.wave_parameters = wa1, wa2, wa3
            transition_from.wave_parameters = wb1, wb2, wb3

    def get_child_objects(self):
        return []

    def process_event(self, event):
        pass

    def update(self, delta_time):
        self.transition_pos += delta_time * self.transition_speed

    def render(self, pad):

        # check, if the pattern needs to be recalculated
        if self.size != self.last_bg_pattern.shape or self.transition_pos < 1.0:
            self.update_bg_pattern()

        # draw
        w, h = self.size
        for x in range(w):
            for y in range(h):

                # get the style for the current "pixel"
                pattern_value = self.last_bg_pattern[x, y]
                if pattern_value > .1:
                    style_character = self.style1_character
                    style_colour_fg = self.style1_colour_fg
                    style_colour_bg = self.style1_colour_bg
                elif pattern_value < -.1:
                    style_character = self.style2_character
                    style_colour_fg = self.style2_colour_fg
                    style_colour_bg = self.style2_colour_bg
                else:
                    style_character = self.border_character
                    style_colour_fg = self.border_colour_fg
                    style_colour_bg = self.border_colour_bg

                # draw
                try:
                    pad.addstr(
                        y, x,
                        style_character,
                        get_colour_pair(*style_colour_fg, *style_colour_bg))
                except curses.error:
                    pass

    def update_bg_pattern(self):

        # reset the pattern
        self.last_bg_pattern = np.zeros(self.size)

        # incorporate transitions
        if self.transition_from is not None and self.transition_pos < 1.0:
            all_wave_parameters = (interpolate_wave_parameters(
                self.transition_pos,
                *self.transition_from.wave_parameters[i],
                *self.wave_parameters[i]
                )
                for i in range(3)
            )
        else:
            all_wave_parameters = self.wave_parameters

        # calculate the pattern
        for wave_params in all_wave_parameters:
            self.last_bg_pattern += eval_wave(*self.size, *wave_params)
        self.last_bg_pattern = self.last_bg_pattern / len(self.wave_parameters)
