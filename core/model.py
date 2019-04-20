import copy
import random

from core.calc import find_best_score
from utils.constants import CARDS
from utils.utils import sort


class GameException(Exception):
    pass


class Model:

    CARDS_PER_PLAYER = 10

    def __init__(self):
        self.score = [0, 0]
        self.knocker_sets = None
        self.stack = None
        self.discard_pile = None
        self.players_cards = None

    def start_game(self):
        self.stack = copy.copy(list(CARDS.keys()))
        random.shuffle(self.stack)
        self.discard_pile = []
        self.players_cards = [[], []]
        for i in range(self.CARDS_PER_PLAYER):
            self.draw_card(0)
            self.draw_card(1)

        self.discard_pile.append(self.stack.pop())

    def draw_card(self, player):
        card = self.stack.pop()
        self.players_cards[player].append(card)
        self.players_cards[player] = sort(self.players_cards[player])

    def steal_card(self, player):
        card = self.discard_pile.pop()
        self.players_cards[player].append(card)

    def discard_card(self, player, card):
        self.players_cards[player] = [c for c in self.players_cards[player] if c != card]
        self.discard_pile.append(card)

    def describe(self, player_id):
        return "{} | {}".format('' if len(self.discard_pile) is 0 else self.discard_pile[-1],
                                ' '.join(self.players_cards[player_id]))

    def count(self, player, is_knocker=True):
        if is_knocker:
            sets, score = find_best_score(self.players_cards[player])
            self.knocker_sets = sets
        else:
            self.players_cards[player] += self.knocker_sets
            _, score = find_best_score(self.players_cards[player])

        return score

    def knock(self, player):
        if not self._can_knock(player):
            raise GameException('Cannot knock unless you have 10 or less points')

        return self._make_difference(player, 0 if player else 1)

    def _can_knock(self, player):
        return self.count(player) <= 10

    def _make_difference(self, knocker, defender):
        win = False
        knocker_count = self.count(knocker)
        defender_count = self.count(defender, is_knocker=False)
        if knocker_count < defender_count:
            if knocker_count == 0:
                self.score[knocker] += 25
                if len(self.players_cards[knocker]) == 11:
                    self.score[knocker] += 6

            self.score[knocker] += defender_count - knocker_count + 10
            win = True
        else:
            self.score[defender] += knocker_count - defender_count + 20

        return win
