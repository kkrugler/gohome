#!/usr/bin/env python
try:
    import sys
    from random import shuffle

    import enums, card, card_holder
except ImportError as err:
    print("Fail loading a module in file:", __file__, "\n", err)
    sys.exit(2)


class Deck(card_holder.CardsHolder):
    """ Deck of cards."""

    def __init__(self, pos, offset, last_card_callback=None):
        """
        :param pos: tuple with coordinates (x, y) for bottom card in the desk
        :param last_card_callback: function that should be called when the last card is
            removed from the deck
        """
        card_holder.CardsHolder.__init__(self, pos, offset, (0, 0),
                                         enums.GrabPolicy.can_grab_top, last_card_callback)

        card_pos = pos
        for persona in range(enums.Persona.first, enums.Persona.last + 1):
            for rank in range(enums.Rank.first, enums.Rank.last + 1):
                for i in range(rank):
                    self.cards.append(card.Card(persona, rank, card_pos, True))
                    card_pos = card_pos[0] + self.offset[0], card_pos[1] + self.offset[1]

    def shuffle(self):
        """ Shuffles cards in the deck randomly """
        shuffle(self.cards)
        self.update_position()
