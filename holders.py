try:
    import sys
    import pygame

    from pygame_cards import card_holder, enums, card
except ImportError as err:
    print("Fail loading a module in file:", __file__, "\n", err)
    sys.exit(2)


def draw_empty_card_pocket(holder, screen):
    """ Renders empty card pocket at the position of CardHolder object
    :param holder: CardsHolder object
    :param screen: Screen object to render onto
    """
    if len(holder.cards) == 0:
        rect = (holder.pos[0], holder.pos[1],
                card_holder.CardsHolder.card_json["size"][0],
                card_holder.CardsHolder.card_json["size"][1])
        pygame.draw.rect(screen, (77, 77, 77), rect, 2)


class GrabbedCardsHolder(card_holder.CardsHolder):
    """Holds cards currently grabbed by the user (ie under the mouse with the button held down)"""
    def add_card(self, card_, on_top=False):
        if isinstance(card_, card.Card):
            if on_top:
                self.cards.append(card_)
            else:
                self.cards.insert(0, card_)

    def render(self, screen):
        if len(self.cards) > 0:
            self.pos = self.cards[0].get_sprite().pos
            self.update_position(self.offset)
            _ = screen


class DeckRevealed(card_holder.CardsHolder):
    """ Container for revealed cards.
    """

    def __init__(self, pos, offset):
        """
        :param pos: tuple with coordinates (x, y) for bottom card in the desk
        """
        super().__init__(pos, offset, enums.GrabPolicy.can_single_grab, None, True)


class CompletedSet(card_holder.CardsHolder):

    def __init__(self, pos, offset):
        """
        :param pos: tuple with coordinates (x, y) for bottom card in the desk
        """
        super().__init__(pos, offset, enums.GrabPolicy.no_grab, None, True)
