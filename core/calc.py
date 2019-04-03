import itertools
import sys
import warnings

import numpy as np

from utils.constants import (
    CARDS,
    VALUES
)
from utils.utils import sort


def find_best_score(cards):
    sets, rest_combinations = find_all_combinations(cards)
    s = []
    score = sys.maxsize

    i = 0
    while i < len(rest_combinations):
        tmp_score = count(rest_combinations[i])
        if score > tmp_score:
            score = tmp_score
            s = sets[i]

        i += 1

    return s, score if score is not sys.maxsize else 0


def find_all_combinations(cards):
    straight_flushes = np.array(find_straight_flushes(cards)).flatten()
    multiples = np.array(find_multiples(cards)).flatten()

    pivots = []
    for card1 in straight_flushes:
        for card2 in multiples:
            if card1 == card2:
                pivots.append(card1)

    tmp_pivot_combinations = []

    for i in range(len(pivots)):
        comb = list(itertools.combinations(pivots, i + 1))
        if len(comb) is 1:
            comb.append(())

        tmp_pivot_combinations.append(comb)

    pivot_combinations = []

    for combination in tmp_pivot_combinations:
        pivot_combinations.append(
            {
                'sf': combination[0],
                'm': combination[1]
            }
        )
        pivot_combinations.append(
            {
                'sf': combination[::-1][0],
                'm': combination[::-1][1]
            }
        )

    dead_cards = []
    sets = []

    if pivot_combinations:
        for pivot_combination in pivot_combinations:
            sf_cards = [card for card in cards if card not in pivot_combination['m']]
            m_cards = [card for card in cards if card not in pivot_combination['sf']]

            tmp_sf = np.array(find_straight_flushes(sf_cards)).flatten().tolist()
            tmp_m = np.array(find_multiples(m_cards)).flatten().tolist()
            dead_cards.append([card for card in cards if card not in tmp_sf and card not in tmp_m])
            sets.append(tmp_m + tmp_sf)
    else:
        with warnings.catch_warnings():
            warnings.simplefilter(action='ignore', category=FutureWarning)
            dead_cards = [list(card for card in cards if card not in straight_flushes and card not in multiples)]
            sets = [list(card for card in cards if card in straight_flushes or card in multiples)]

    return sets, dead_cards


def count(cards):
    score = 0
    for card in cards:
        score += min(CARDS[card], 10)

    return score


def find_straight_flushes(cards):
    result = []

    cards_by_color = {
        'd': [],
        'h': [],
        's': [],
        'c': []
    }

    for card in cards:
        color = card[-1]
        cards_by_color[color].append(CARDS[card])

    for color, values in cards_by_color.items():
        values = sort(values)
        cards_by_color[color] = [straight for straight in find_straights(values)]

    for color, straights in cards_by_color.items():
        for straight in straights:
            result.append([VALUES[value] + color for value in straight])

    return result


def find_straights(cards):
    result = []
    start = 1
    while start < len(cards):
        cards_in_a_row = start
        while cards_in_a_row < len(cards) and cards[cards_in_a_row] - cards[cards_in_a_row - 1] is 1:
            cards_in_a_row += 1

        if cards_in_a_row - start + 1 >= 3:
            result.append([cards[i] for i in range(start - 1, cards_in_a_row)])

        start = cards_in_a_row + 1

    return result


def find_multiples(cards):
    result = []
    multiples = [[] for _ in range(13)]
    cards = sort(cards)

    for card in cards:
        multiples[CARDS[card] - 1].append(card)

    for m in multiples:
        if len(m) >= 3:
            for value in m:
                result.append(value)

    return result
