#!/usr/bin/env python
try:
    import sys
    import operator

    import game_object, card, enums
except ImportError as err:
    print("Fail loading a module in file:", __file__, "\n", err)
    sys.exit(2)


class CardsHolder(game_object.GameObject):
    """ Card holder, to which cards can be added and from which cards can be grabbed and moved
    to other cards holders. Ex.: a deck of cards, a player's pile of cards.
    Can be inherited and modified/extended for specific needs.

    Attributes:
        card_json - The 'card' node of the settings.json. Data can be accessed via [] operator,
                    for example: CardsHolder.card_json["size"][0]
    """

    card_json = None

    def __init__(self, pos=(0, 0), offset=(0, 0), limit=(0, 0),
                 grab_policy=enums.GrabPolicy.no_grab_or_click, last_card_callback=None, refill=False):
        """
        :param pos: tuple with coordinates (x, y) - position of top left corner of cards holder
        :param offset: tuple (x, y) with values of offset between cards in the holder
        :param grab_policy: value from enums.GrabPolicy (by default enums.GrabPolicy.no_grab)
        :param last_card_callback: function to be called once the last card removed (default None)
        """
        self.cards = []
        game_object.GameObject.__init__(self, self.cards, grab_policy)
        self.last_card_callback = last_card_callback
        self.pos = pos
        self.offset = offset
        self.limit = limit
        self.refill = refill

    def is_empty(self):
        return len(self.cards) is 0

    def is_clicked(self, pos):
        """ Checks if a top card is clicked.
        :param pos: tuple with coordinates (x, y) - position of mouse click/screen touch.
        :return: True if top card is clicked, False otherwise
        """
        if len(self.cards) is not 0:
            if self.cards[-1].is_clicked(pos):
                return True
        elif pos[0] > self.pos[0] and pos[0] < (self.pos[0] + CardsHolder.card_json["size"][0]) and\
             pos[1] > self.pos[1] and pos[1] < (self.pos[1] + CardsHolder.card_json["size"][1]):
            return True
        else:
            return False

    def find_clicked_card(self, pos):
        """ Tries to grab a card (or multiple cards) with a mouse click.
        :param pos: tuple with coordinates (x, y) - position of mouse click/screen touch.
        :return: Card object if grabbed or None if card can't be grabbed or mouse click
                 is not on the holder.
        """
        if (self.grab_policy == enums.GrabPolicy.no_grab_or_click) or (len(self.cards) == 0):
            return None

        if self.grab_policy == enums.GrabPolicy.can_grab_top:
            top_card = self.cards[-1]
            if top_card.is_clicked(pos):
                return self.pop_top_card()
            else:
                return None

        clicked_card = None
        for card_ in self.cards:
            if card_.is_clicked(pos):
                clicked_card = card_

        return clicked_card

    def add_card(self, card_, on_top=True):
        """ Appends a card to the list of self.cards
        :param card_:  object of the Card class to be appended to the list
        :param on_top: boolean, True if the card should be put on top, False in the bottom
        """
        card_.unclick()
        if on_top:
            pos_ = self.pos
            if len(self.cards) is not 0:
                length = len(self.cards)
                pos_ = (self.pos[0] + length * self.offset[0],
                        self.pos[1] + length * self.offset[1])
            card_.set_pos(pos_)
            self.cards.append(card_)
        else:
            self.cards.insert(0, card_)
            self.update_position()

    def remove_card(self, card):
        index = self.cards.index(card)
        self.cards.pop(index)

    def pop_card(self, top):
        """ Removes top or bottom cards from the list and returns it.
        :param top: boolean, if True top card is removed, otherwise bottom card is removed.
        :return: Card object
        """
        if len(self.cards) == 0:
            return None
        else:
            if len(self.cards) == 1 and self.last_card_callback is not None:
                self.last_card_callback(self.cards[0])


            if top:
                result = self.cards.pop()
            else:
                result = self.cards.pop(0)

            # Update positions in case we can spread things out now
            self.update_position()
            return result

    def pop_top_card(self):
        """ Removes top card from the list and returns it.
        If there are no cards left, returns None.
        :return: Card object
        """
        return self.pop_card(top=True)

    def pop_bottom_card(self):
        """ Removes last card from the list and returns it.
        If there are no cards left, returns None.
        :return: Card object
        """
        return self.pop_card(top=False)

    def flip_cards(self):
        """ Flip cards from face-up to face-down and vice versa """
        for card_ in self.cards:
            card_.flip()

    def sort_cards(self):
        """ Sort cards by persona and rank from lower to higher.
        Persona order by enum order.
        After sorting, re-do positions
        """
        self.cards.sort(key=operator.attrgetter('persona', 'rank'))
        self.update_position()

    def move_all_cards(self, other, back_side_up=True):
        """ Moves all cards to other cards holder.
        :param other: instance of CardsHolder where cards will be moved.
        :param back_side_up: True if cards should be flipped to back side up, False otherwise.
        """
        if isinstance(other, CardsHolder):
            while len(self.cards) != 0:
                card_ = self.pop_top_card()
                if card_ is not None:
                    if card_.back_up != back_side_up:
                        card_.flip()
                    other.add_card(card_)

    def update_position(self):
        """ Updates position of all cards
        """

        if not self.cards:
            return

        # First see if we need to reduce our offset in order to
        # constrain to the limit.
        x_offset = self.offset[0]
        if self.limit[0] != 0:
            max_x_range = self.limit[0] - self.pos[0]
            max_x_offset = max_x_range / len(self.cards)
            x_offset = min(x_offset, max_x_offset)

        y_offset = self.offset[1];
        if self.limit[1] != 0:
            max_y_range = self.limit[1] - self.pos[1]
            max_y_offset = max_y_range / len(self.cards)
            y_offset = min(y_offset, max_y_offset)

        pos_ = self.pos
        for card_ in self.cards:
            card_.set_pos(pos_)
            pos_ = pos_[0] + x_offset, pos_[1] + y_offset

    def check_collide(self, card_):
        """ Checks if current cards holder collides with other card.
        :param card_: Card object to check collision with
        :return: True if card collides with holder, False otherwise
        """
        if len(self.cards) > 0:
            return self.cards[-1].check_collide(card_=card_)
        else:
            return card_.check_collide(pos=self.pos)

    def render(self, screen):
        """ Does not render anything by default.
        Should be overridden in derived classes if need to render anything for the holder itself.
        Cards in the holder are rendered by higher level render_all().
        :param screen: Screen to render objects on
        """
        pass
