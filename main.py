#!/usr/bin/env python
try:
    import sys
    import os
    from random import choice
    import pygame

    from pygame_cards import controller, game_app, deck, card_holder, enums, card
    from enums import GameState
    import holders
    import player
    import personas

except ImportError as err:
    print("Fail loading a module in file:", __file__, "\n", err)
    sys.exit(2)


class GoHomeController(controller.Controller):

    def __init__(self):
        super().__init__()

    '''
    One-time setup of game environment
    '''
    def build_objects(self):
        # Set up music
        music = os.path.join(os.getcwd(), 'data/fish.wav')
        pygame.mixer.music.load(music)

        # Set up state machine
        self.game_states = self.create_game_states()

        # TODO figure out how this gets invoked.
        setattr(deck.Deck, "render", holders.draw_empty_card_pocket)

        deck_pos = self.settings_json["deck"]["position"]
        deck_offset = self.settings_json["deck"]["offset"]
        self.deck = deck.Deck(deck_pos, deck_offset, None)
        self.add_rendered_object(self.deck)

        revealed_pos = self.settings_json["revealed"]["position"]
        revealed_offset = self.settings_json["revealed"]["offset"]
        self.revealed = [None] * 3

        for i in range(3):
            self.revealed[i] = holders.DeckRevealed(revealed_pos, revealed_offset)
            self.add_rendered_object(self.revealed[i])
            revealed_pos = (revealed_pos[0] + revealed_offset[0], revealed_pos[1] + revealed_offset[1])

        computer_pos = self.settings_json["computer_hand"]["position"]
        computer_offset = self.settings_json["computer_hand"]["offset"]
        computer_limit = self.settings_json["computer_hand"]["limit"]
        self.computer_hand = player.ComputerHand(computer_pos, computer_offset, computer_limit)
        self.add_rendered_object(self.computer_hand)

        self.personas = personas.Personas()
        cards_pos = self.settings_json["user_persona"]["position"]
        self.user_persona = self.personas.next_persona()
        self.user_persona.set_pos(cards_pos)
        self.add_rendered_object(self.user_persona)

        cards_pos = self.settings_json["computer_persona"]["position"]
        self.computer_persona = self.personas.next_persona()
        self.computer_persona.set_pos(cards_pos)
        # Don't show user the computer's persona
        self.computer_persona.flip()
        self.add_rendered_object(self.computer_persona)

        cards_pos = self.settings_json["user_hand"]["position"]
        cards_offset = self.settings_json["user_hand"]["offset"]
        cards_limit = self.settings_json["user_hand"]["limit"]
        self.user_hand = player.UserHand(cards_pos, cards_offset, cards_limit)
        self.add_rendered_object(self.user_hand)

        cards_pos = self.settings_json["user_sets"]["position"]
        cards_offset = self.settings_json["user_sets"]["offset"]
        cards_limit = self.settings_json["user_sets"]["limit"]
        self.user_sets = holders.CompletedSet(cards_pos, cards_offset, cards_limit)
        self.add_rendered_object(self.user_sets)

        cards_pos = self.settings_json["computer_sets"]["position"]
        cards_offset = self.settings_json["computer_sets"]["offset"]
        cards_limit = self.settings_json["computer_sets"]["limit"]
        self.computer_sets = holders.CompletedSet(cards_pos, cards_offset, cards_limit)
        self.add_rendered_object(self.computer_sets)

        self.gui_interface.show_button(self.settings_json["gui"]["restart_button"],
                                       self.restart_game, "Restart")

    def restart_game(self):
        pygame.mixer.music.rewind()

        self.revealed.move_all_cards(self.deck)
        self.user_hand.move_all_cards(self.deck)
        self.user_sets.move_all_cards(self.deck)
        self.computer_hand.move_all_cards(self.deck)
        self.computer_sets.move_all_cards(self.deck)

        if isinstance(self.gui_interface, game_app.GameApp.GuiInterface):
            self.gui_interface.hide_by_id("win_label1")
            self.gui_interface.hide_by_id("win_label2")

        self.start_game()

    def start_game(self):

        self.deck.shuffle()
        # self.deal_cards()

        self.state = GameState.starting
        self.state_time = pygame.time.get_ticks()

        for i in range(3):
            card_ = self.deck.pop_top_card()
            card_.flip()
            self.revealed[i].add_card(card_)

        for i in range(7):
            card_ = self.deck.pop_top_card()
            card_.flip()
            self.user_hand.add_card(card_)

            card_ = self.deck.pop_top_card()
            self.computer_hand.add_card(card_)

        self.user_hand.sort_cards()
        self.check_for_sets(self.user_hand, self.user_sets)

        self.computer_hand.sort_cards()
        self.check_for_sets(self.computer_hand, self.computer_sets)

        self.custom_dict["game_start_time"] = pygame.time.get_ticks()
        pygame.mixer.music.play(-1)

        self.next_state(choice((enums.GameState.user_turn, enums.GameState.computer_turn)))

    def next_state(self, new_state):
        if (new_state != self.state):
            self.state = new_state
            self.state_time = pygame.time.get_ticks()

            func = self.game_states[new_state]
            func(self, True)

    def check_for_sets(self, hand, set):
        new_sets = hand.find_sets()
        for card in new_sets:
            card.reveal()
            set.add_card(card)
            set.update_position()

    def check_win(self):
        if (self.state == GameState.done) or (self.state == GameState.starting):
            return

        done = self.deck.is_empty() and self.revealed[0].is_empty() and self.revealed[1].is_empty() and \
               self.revealed[2].is_empty()
        if done:
            self.computer_persona.reveal()

            user_points = self.user_sets.calc_score(self.user_persona)
            computer_points = self.computer_sets.calc_score(self.computer_persona)

            if user_points > computer_points:
                self.set_user_text("User won, %d to %d" % (user_points, computer_points))
            elif (computer_points > user_points):
                self.set_computer_text("Computer won, %d to %d" % (computer_points, user_points))
            else:
                self.set_user_text("User & computer tied with %d points" % user_points)

            self.next_state(GameState.done)

    def execute_game(self):
        # See if all of the cards are out. If so, calculate the winner and go to game over state
        self.check_win()

        func = self.game_states[self.state]
        func(self)

    def process_mouse_event(self, pos, down, double_click=False):
        if down:
            self.process_mouse_down(pos)
        else:
            self.process_mouse_up(pos)

        if double_click:
            self.process_double_click(pos)

    def process_mouse_down(self, pos):
        if self.state != GameState.user_turn:
            # TODO still allow click on restart button
            # TODO play noise
            return

        for obj in self.rendered_objects:
            if not obj.can_grab() and not obj.can_click():
                continue

            if obj.can_grab():
                grabbed_card = obj.find_clicked_card(pos)
                if grabbed_card is not None:
                    grabbed_card.reveal()
                    '''
                    self.add_move([grabbed_card], self.user_hand.get_end_pos())
                    self.user_moving_cards = grabbed_card
                    '''
                    self.user_hand.add_card(grabbed_card, True)
                    self.user_hand.sort_cards()
                    self.check_for_sets(self.user_hand, self.user_sets)

                    if obj.refill:
                        self.set_user_text("User picked from the up cards")
                        self.refill_revealed(obj)
                    else:
                        self.set_user_text("User picked from the deck")

                    self.next_state(GameState.user_picking)
                    break
            elif obj.can_click():
                clicked_card = obj.find_clicked_card(pos)
                if clicked_card is not None:
                    # Ask the computer for its cards.
                    stolen_cards = self.computer_hand.steal_cards(clicked_card)
                    if stolen_cards:
                        self.computer_hand.update_position();

                        for stolen_card in stolen_cards:
                            stolen_card.flip()
                            self.user_hand.add_card(stolen_card, True)

                        self.set_user_text("User stole from the computer")
                        self.user_hand.sort_cards()
                        self.check_for_sets(self.user_hand, self.user_sets)
                    else:
                        self.set_user_text("User tried to steal from the computer")

                    self.next_state(GameState.user_stealing)


    def refill_revealed(self, stack):
        if not self.deck.is_empty():
            deck_card = self.deck.pop_top_card()
            deck_card.reveal()
            stack.add_card(deck_card, True)

    def process_mouse_up(self, pos):
        return

    def process_double_click(self, pos):
        return

    def cleanup(self):
        pygame.mixer.music.stop()

    def set_user_text(self, text):
        self.gui_interface.hide_by_id("user_text")
        if text is not None:
            self.set_computer_text(None)
            pos = self.settings_json["user_text"]["position"]
            self.gui_interface.show_label(position=pos, text=text, text_size=30, timeout=0,
                                          id_="user_text")

    def set_computer_text(self, text):
        self.gui_interface.hide_by_id("computer_text")
        if text is not None:
            self.set_user_text(None)
            pos = self.settings_json["computer_text"]["position"]
            self.gui_interface.show_label(position=pos, text=text, text_size=30, timeout=0,
                                          id_="computer_text")

    def user_turn_state(self, init=False):
        if init:
            self.set_user_text("Yo, it's your turn!")

        return
        '''
        remaining_time = (self.state_time + 300) - pygame.time.get_ticks()
        if remaining_time < 0:
            self.set_user_text("Time's up!")
            self.computer_turn_state(True)
        elif remaining_time < 120:
            self.set_user_text("Time is running out!")
        '''

    def user_picking_state(self, init=False):
        # Wait until the card(s) have been moved.
        '''
        if not self.has_moves():
            self.user_hand.add_card(self.user_moving_cards, True)
            self.user_moving_cards = None

            self.user_hand.sort_cards()
            self.check_for_sets(self.user_hand, self.user_sets)

            self.next_state(GameState.computer_turn)
        '''
        if init:
            self.next_state_time = self.state_time + 2000
        elif pygame.time.get_ticks() >= self.next_state_time:
            self.next_state(GameState.computer_turn)

    def user_stealing_state(self, init=False):
        if init:
            self.next_state_time = self.state_time + 2000
        elif pygame.time.get_ticks() >= self.next_state_time:
            self.next_state(GameState.computer_turn)

    def computer_turn_state(self, init=False):
        if init:
            while True:
                index = choice((0, 1, 2, 3, 4, 5, 6, 7))
                if (index == 3) or (index == 4):
                    # Try to steal from the user
                    if not self.user_hand.is_empty():
                        target_card = choice(self.computer_hand.cards)
                        stolen_cards = self.user_hand.steal_cards(target_card)
                        if stolen_cards:
                            self.user_hand.update_position()

                            for stolen_card in stolen_cards:
                                stolen_card.flip()
                                self.computer_hand.add_card(stolen_card, True)

                            self.set_computer_text("Computer stole from the user")
                            self.computer_hand.sort_cards()
                            self.check_for_sets(self.computer_hand, self.computer_sets)
                        else:
                            self.set_computer_text("Computer tried to steal from the user")

                        self.next_state(GameState.computer_stealing)
                        break
                elif index >= 5:
                    if not self.deck.is_empty():
                        grabbed_card = self.deck.pop_top_card()
                        self.computer_hand.add_card(grabbed_card, True)
                        self.computer_hand.sort_cards()
                        self.check_for_sets(self.computer_hand, self.computer_sets)
                        self.set_computer_text("I'm grabbing from the deck")
                        self.next_state(GameState.computer_picking)
                        break
                else:
                    stack = self.revealed[index]
                    if not stack.is_empty():
                        grabbed_card = stack.pop_top_card()
                        grabbed_card.flip()

                        self.computer_hand.add_card(grabbed_card, True)
                        self.computer_hand.sort_cards()
                        self.check_for_sets(self.computer_hand, self.computer_sets)

                        self.set_computer_text("I'm grabbing from the up cards")
                        self.next_state(GameState.computer_picking)

                        self.refill_revealed(stack)

                        break


    def computer_picking_state(self, init=False):
        if init:
            self.next_state_time = self.state_time + 2000
        elif pygame.time.get_ticks() >= self.next_state_time:
            self.next_state(GameState.user_turn)

    def computer_stealing_state(self, init=False):
        if init:
            self.next_state_time = self.state_time + 2000
        elif pygame.time.get_ticks() >= self.next_state_time:
            self.next_state(GameState.user_turn)

    def starting_state(self, init=False):
        if init:
            self.restart_game()

    def done_state(self, init=False):
        if init:
            self.next_state_time = self.state_time + 10000
        elif pygame.time.get_ticks() >= self.next_state_time:
            self.next_state(GameState.starting)

    def create_game_states(self):
        return {
            GameState.starting: GoHomeController.starting_state,

            GameState.user_turn: GoHomeController.user_turn_state,
            GameState.user_picking: GoHomeController.user_picking_state,
            GameState.user_stealing: GoHomeController.user_stealing_state,

            GameState.computer_turn: GoHomeController.computer_turn_state,
            GameState.computer_picking: GoHomeController.computer_picking_state,
            GameState.computer_stealing: GoHomeController.computer_stealing_state,

            GameState.done: GoHomeController.done_state,

        }

def main():
    json_path = os.path.join(os.getcwd(), 'settings.json')
    klondike_app = game_app.GameApp(json_path=json_path, game_controller=GoHomeController())
    klondike_app.execute()

if __name__ == '__main__':
    main()
