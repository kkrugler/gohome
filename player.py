try:
    import sys

    from pygame_cards import card_holder, enums, card
except ImportError as err:
    print("Fail loading a module in file:", __file__, "\n", err)
    sys.exit(2)


class PlayerHand(card_holder.CardsHolder):

    def __init__(self, pos, offset, limit=(0,0)):
        super().__init__(pos, offset, limit)

    def add_cards(self, cards):
        for card in cards:
            self.add_card(card, True)

    def steal_cards(self, card):
        '''
        If we have any of <card> in our hand, we have to return them.

        :param card:
        :return: list of cards, or empty list
        '''

        result = []
        offset = 0
        while offset < len(self.cards):
            my_card = self.cards[offset]
            if my_card == card:
                result.append(self.cards.pop(offset))
            else:
                offset += 1

        return result

    def find_sets(self):
        '''
        Find any complete set (all cards of same rank from same persona) and return one card
        for each such set. We assume the hand is sorted!!!
        :return: list of cards. List is empty if there are no sets
        '''
        result = []
        first_in_set = None
        num_in_set = 0
        for card in self.cards:
            if first_in_set is None:
                first_in_set = card
                num_in_set = 1
            elif card != first_in_set:
                # if (num_in_set == first_in_set.rank):
                if (num_in_set == 3):
                    result.append(first_in_set)

                first_in_set = card
                num_in_set = 1
            else:
                num_in_set += 1

        if (first_in_set is not None) & (num_in_set == 3):
            result.append(first_in_set)

        # Now we have to remove all of these sets from our hand.
        if result:
            offset = 0
            while offset < len(self.cards):
                card = self.cards[offset]
                in_result = False
                for set_card in result:
                    if card == set_card:
                        in_result = True
                        break;

                if in_result:
                    self.cards.pop(offset)
                else:
                    offset += 1

            self.update_position()

        return result

class UserHand(PlayerHand):

    def __init__(self, pos, offset, limit):
        super().__init__(pos, offset, limit)

class ComputerHand(PlayerHand):

    def make_play(self, deck, revealed):
        '''
        Decide whether to get one of the face-up cards, or draw from the deck, or steal
        from the player.
        :return: Tuple with ("deck"), ("revealed", <index>), ("player", <card>)
        '''


        return ("deck")
