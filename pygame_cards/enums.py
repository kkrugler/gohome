#!/usr/bin/env python
try:
    import sys
    #from enum import IntEnum
except ImportError as err:
    print("Fail loading a module in file:", __file__, "\n", err)
    sys.exit(2)


class Rank:
    """ Enums for cards' ranks, which also corresponds to the number for a set, and points """
    persona = 0

    first = 2
    two = first
    three = 3
    four = 4
    last = four


class Persona:
    """ Enums for cards' personas """
    first = 0
    neatfreak = first
    gymguy = neatfreak + 1
    bookworm = gymguy + 1
    catlady = bookworm + 1
    girlygirl = catlady + 1
    gamerguy = girlygirl + 1
    hippydude = gamerguy + 1
    last = hippydude


class GrabPolicy:
    """ Enums for different grab policies of cards' holders."""
    no_grab_or_click = 0
    can_grab_top = 1
    can_click_any = 2

class GameState:
    starting = -1
    user_turn = 0
    user_picking = 1
    user_stealing = 2
    computer_turn = 3
    computer_picking = 4
    computer_stealing = 5
    done = 6


