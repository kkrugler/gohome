#!/usr/bin/env python
try:
    import sys
    import os
    import pygame

    from pygame_cards import controller, game_app, deck, card_holder, enums, card
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

        # TODO figure out how this gets invoked.
        setattr(deck.Deck, "render", holders.draw_empty_card_pocket)

        deck_pos = self.settings_json["deck"]["position"]
        deck_offset = self.settings_json["deck"]["offset"]
        self.deck = deck.Deck(deck_pos, deck_offset, None)
        self.add_rendered_object(self.deck)

        revealed_pos = self.settings_json["revealed"]["position"]
        revealed_offset = self.settings_json["revealed"]["offset"]
        self.custom_dict["revealed"] = [None] * 3

        for i in range(3):
            self.custom_dict["revealed"][i] = holders.DeckRevealed(revealed_pos, revealed_offset)
            self.add_rendered_object(self.custom_dict["revealed"][i])
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

        self.custom_dict["revealed"].move_all_cards(self.deck)
        self.user_hand.move_all_cards(self.deck)

        if isinstance(self.gui_interface, game_app.GameApp.GuiInterface):
            self.gui_interface.hide_by_id("win_label1")
            self.gui_interface.hide_by_id("win_label2")

        self.start_game()

    def start_game(self):

        self.deck.shuffle()
        # self.deal_cards()

        for i in range(3):
            card_ = self.deck.pop_top_card()
            card_.flip()
            self.custom_dict["revealed"][i].add_card(card_)

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

    def check_for_sets(self, hand, set):
        new_sets = hand.find_sets()
        for card in new_sets:
            set.add_card(card)
            set.update_position()

    def check_win(self):
        win = False
        if win:
            self.show_win_ui()

    def show_win_ui(self):
        text = "You won, congrats!"
        pos = self.settings_json["gui"]["win_label"]
        size = self.settings_json["gui"]["win_text_size"]
        self.gui_interface.show_label(position=pos, text=text, text_size=size, timeout=0,
                                      id_="win_label1")
        if hasattr(self, "game_start_time") and self.custom_dict["game_start_time"] is not None:
            total_seconds = (pygame.time.get_ticks() - self.custom_dict["game_start_time"])/1000
            minutes = str(total_seconds / 60)
            seconds = str(total_seconds % 60)
            if len(seconds) == 1:
                seconds = "0" + seconds
            game_time = str(minutes) + ":" + str(seconds)
            text = "Game time: " + str(game_time)
            pos = pos[0], pos[1] + size
            self.gui_interface.show_label(position=pos, text=text, text_size=size, timeout=0,
                                          id_="win_label2")

    def execute_game(self):
        pass

    def process_mouse_event(self, pos, down, double_click=False):
        if down:
            self.process_mouse_down(pos)
        else:
            self.process_mouse_up(pos)

        if double_click:
            self.process_double_click(pos)

    def process_mouse_down(self, pos):
        for obj in self.rendered_objects:
            if not obj.can_grab():
                continue

            grabbed_cards = obj.try_grab_card(pos)
            if grabbed_cards is not None:
                for card_ in grabbed_cards:
                    if card_.back_up:
                        card_.flip()

                    self.user_hand.add_card(card_, True)

                self.user_hand.sort_cards()
                self.check_for_sets(self.user_hand, self.user_sets)

                if obj.refill and (not self.deck.is_empty()):
                    deck_card = self.deck.pop_top_card()
                    deck_card.flip()
                    obj.add_card(deck_card, True)

                break

    def process_mouse_up(self, pos):
        return

    def process_double_click(self, pos):
        return

    def cleanup(self):
        pygame.mixer.music.stop()

def main():
    json_path = os.path.join(os.getcwd(), 'settings.json')
    klondike_app = game_app.GameApp(json_path=json_path, game_controller=GoHomeController())
    klondike_app.execute()

if __name__ == '__main__':
    main()
