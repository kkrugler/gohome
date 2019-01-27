try:
    import sys
    from random import shuffle

    from pygame_cards import enums, card
except ImportError as err:
    print("Fail loading a module in file:", __file__, "\n", err)
    sys.exit(2)

class Personas:

    def __init__(self):
        self.personas = []
        for persona in range(enums.Persona.first, enums.Persona.last + 1):
            self.personas.append(card.Card(persona, enums.Rank.persona, (0, 0), False))

        shuffle(self.personas)

    def next_persona(self):
        return self.personas.pop()