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


class DeckRevealed(card_holder.CardsHolder):
    """ Container for revealed cards.
    """

    def __init__(self, pos, offset):
        """
        :param pos: tuple with coordinates (x, y) for bottom card in the desk
        """
        super().__init__(pos, offset, (0, 0), enums.GrabPolicy.can_grab_top, None, True)


class CompletedSet(card_holder.CardsHolder):

    def __init__(self, pos, offset, limit):
        """
        :param pos: tuple with coordinates (x, y) for bottom card in the desk
        """
        super().__init__(pos, offset, limit, enums.GrabPolicy.no_grab_or_click, None, True)

    def calc_score(self, persona):
        score = 0
        for card in self.cards:
            set_score = card.rank
            if card.persona == persona.persona:
                set_score *= 2
            score += set_score

        return score