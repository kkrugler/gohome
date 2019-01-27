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

    first = 3
    three = first
    four = 4
    five = 5
    last = five


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
    no_grab = 0,
    can_single_grab = 1,
    can_multi_grab = 2

