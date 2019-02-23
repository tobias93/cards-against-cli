"""
Various layout helpers, that help to position game objects.
"""

from typing import List, Callable, Any, Union
from abc import ABC, abstractmethod

from cac.client.engine.game_object import GameObject


class Layout(ABC):
    """
    A layout basically describes a recrangular area of where to put something (usually a game object).

    The general idea is that layouts can be nested to describe a hierarchy of how space is partitioned.

    Each layout has a minimum size, that it needs to show all of its contents. Parents should respect this minimum
    size by giving the layout at least the space that it needs, if possible.
    Each layout is given an AABB from its parent, that it must be fully contained in.
    """

    @property
    @abstractmethod
    def min_size(self):
        pass

    @abstractmethod
    def apply(self, parent_x, parent_y, parent_w, parent_h):
        pass

    def applyParent(self, parent: GameObject):
        w, h = parent.size
        self.apply(0, 0, w, h)


class Layers(Layout):
    """
    Combines multiple layouts into a single one such that all of
    them share the same parent.
    """

    def __init__(self, *children: Layout):
        super().__init__()
        self._children = children

    @property
    def min_size(self):
        min_w = 0
        min_h = 0
        for child in self._children:
            child_min_w, child_min_h = child.min_size
            min_w = max(min_w, child_min_w)
            min_h = max(min_h, child_min_h)
        return min_w, min_h

    def apply(self, parent_x, parent_y, parent_w, parent_h):
        for child in self._children:
            child.apply(parent_x, parent_y, parent_w, parent_h)
            

class Margin(Layout):
    """
    Adds some additional margins between a parent and a child layout.

    +---------------------------------------------------------+
    |                     :                                   |
    |                     :margin top                         |
    |                     :                                   |
    |                 +--------------------+                  |
    |   margin left   |Child               |   margin right   |
    |·················|                    |··················|
    |                 |                    |                  |
    |                 +--------------------+                  |
    |                     :                                   |
    |                     :margin bottom                      |
    |                     :                                   |
    +---------------------------------------------------------+

    """

    def __init__(self, child: Layout, left=None, top=None, right=None, bottom=None, horizontal=None, vertical=None, margin=0):
        super().__init__()
        horizontal = margin if horizontal is None else horizontal
        vertical = margin if vertical is None else vertical
        left = horizontal if left is None else left
        right = horizontal if right is None else right
        top = vertical if top is None else top
        bottom = vertical if bottom is None else bottom
        self._margin_left = left
        self._margin_top = top
        self._margin_right = right
        self._margin_bottom = bottom
        self._child = child

    @property
    def min_size(self):
        w, h = self._child.min_size
        w += self._margin_left + self._margin_right
        h += self._margin_top + self._margin_bottom
        return w, h

    def apply(self, parent_x, parent_y, parent_w, parent_h):
        child_x = parent_x + self._margin_left
        child_y = parent_y + self._margin_top
        child_w = max(0, parent_w - self._margin_left - self._margin_right)
        child_h = max(0, parent_h - self._margin_top - self._margin_bottom)
        self._child.apply(child_x, child_y, child_w, child_h)


class SoftMargin(Layout):
    """
    Adds some additional margins between a parent and a child layout.
    If the parent shrinks too small, the margin is reduced.

    +---------------------------------------------------------+
    |                     :                                   |
    |                     :margin top                         |
    |                     :                                   |
    |                 +--------------------+                  |
    |   margin left   |Child               |   margin right   |
    |·················|                    |··················|
    |                 |                    |                  |
    |                 +--------------------+                  |
    |                     :                                   |
    |                     :margin bottom                      |
    |                     :                                   |
    +---------------------------------------------------------+

    """

    def __init__(self, child: Layout, left=None, top=None, right=None, bottom=None, horizontal=None, vertical=None, margin=0):
        super().__init__()
        horizontal = margin if horizontal is None else horizontal
        vertical = margin if vertical is None else vertical
        left = horizontal if left is None else left
        right = horizontal if right is None else right
        top = vertical if top is None else top
        bottom = vertical if bottom is None else bottom
        self._margin_left = left
        self._margin_top = top
        self._margin_right = right
        self._margin_bottom = bottom
        self._child = child

    @property
    def min_size(self):
        return self._child.min_size

    def apply(self, parent_x, parent_y, parent_w, parent_h):
        c_min_w, c_min_h = self._child.min_size
        space_x = parent_w - c_min_w           # 🚀
        space_y = parent_h - c_min_h
        if space_x >= (self._margin_left + self._margin_right):
            space_left = self._margin_left
            space_right = self._margin_right
        else:
            space_left = int(space_x / (self._margin_left + self._margin_right) * self._margin_left)
            space_right = space_x - space_left
        if space_y >= (self._margin_top + self._margin_bottom):
            space_top = self._margin_top
            space_bottom = self._margin_bottom
        else:
            space_top = int(space_y / (self._margin_top + self._margin_bottom) * self._margin_top)
            space_bottom = space_y - space_top

        child_x = parent_x + space_left
        child_y = parent_y + space_top
        child_w = parent_w - space_left - space_right
        child_h = parent_h - space_top - space_bottom
        self._child.apply(child_x, child_y, child_w, child_h)


class Size(Layout):
    """
    Centers a layout inside of its parent.

    +------------------------------------------------+
    |                                                |
    |                                                |
    |          +--------------------------+          |
    |          |Child     :               |          |
    |          |          :height         |          |
    |          |          :               |          |
    |          |          :     width     |          |
    |          |··········:···············|          |
    |          |          :               |          |
    |          +--------------------------+          |
    |                                                |
    |                                                |
    +------------------------------------------------+

    """

    def __init__(self, child: Layout, pos_x=.5, pos_y=.5, width=0, height=0):
        self._pos_h = pos_x
        self._pos_v = pos_y
        self._child = child
        self._preferred_width = width
        self._preferred_height = height        

    @property
    def min_size(self):
        return self._child.min_size
    
    def apply(self, parent_x, parent_y, parent_w, parent_h):
        pref_w = self._preferred_width
        pref_h = self._preferred_height
        if isinstance(pref_w, float):
            pref_w = int(pref_w * parent_w)
        if isinstance(pref_h, float):
            pref_h = int(pref_h * parent_h)
        min_w, min_h = self._child.min_size
        w = min(max(pref_w, min_w), parent_w)
        h = min(max(pref_h, min_h), parent_h)
        x = parent_x + int((parent_w - w) * self._pos_h)
        y = parent_y + int((parent_h - h) * self._pos_v)
        self._child.apply(x, y, w, h)


class Vertical(Layout):
    """
    Vertical arrangement of multiple child layouts.

    +---------------------+
    |Child 0              |
    |                     |
    |                     |
    |                     |
    |                     |
    +---------------------+
    |Child 1              |
    +---------------------+
    |Child 2              |
    +---------------------+
    |Child 3              |
    +---------------------+

    """

    def __init__(self, main:int, *children: Layout):
        self._children = children
        self._main = main

    @property
    def min_size(self):
        min_w = 0
        min_h = 0
        for child in self._children:
            child_min_w, child_min_h = child.min_size
            min_w = max(min_w, child_min_w)
            min_h += child_min_h
        return min_w, min_h 

    def apply(self, parent_x, parent_y, parent_w, parent_h):
        min_w, min_h = self.min_size
        additional_height = parent_h - min_h

        pos_y = parent_y
        for i, child in enumerate(self._children):
            child_min_w, child_min_h = child.min_size
            x = parent_x
            y = pos_y
            w = parent_w
            h = child_min_h
            if i == self._main:
                h += additional_height
            child.apply(x, y, w, h)
            pos_y += h


class Place(Layout):

    def __init__(self, child: Union[GameObject, Callable[[int, int, int, int], Any]], min_width=0, min_height=0):
        super().__init__()
        self._child = child
        self._min_w = min_width
        self._min_h = min_height

    @property
    def min_size(self):
        return self._min_w, self._min_h

    def apply(self, parent_x, parent_y, parent_w, parent_h):
        if isinstance(self._child, GameObject):
            self._child.position = parent_x, parent_y
            self._child.size = parent_w, parent_h
        else:
            self._child(parent_x, parent_y, parent_w, parent_h)

