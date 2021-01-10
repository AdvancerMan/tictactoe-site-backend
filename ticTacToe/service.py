import os
import pickle
from functools import lru_cache
from io import BytesIO

import numpy
from PIL import Image

from backend.settings import BASE_DIR


def check_captured(last_i, last_j, game, captured):
    for step_i in range(-1, 2):
        for step_j in range(-1, 2):
            if (captured[step_i + 1][step_j + 1]
                    + captured[-step_i + 1][-step_j + 1] + 1
                    >= game.win_threshold):
                start_i = last_i + step_i * captured[step_i + 1][step_j + 1]
                start_j = last_j + step_j * captured[step_i + 1][step_j + 1]
                return {
                    'start_i': start_i,
                    'start_j': start_j,
                    'direction_i': -step_i,
                    'direction_j': -step_j,
                }


def check_win_field(last_i, last_j, game):
    captured = [[0] * 3 for _ in range(3)]
    for step_i in range(-1, 2):
        for step_j in range(-1, 2):
            if step_i == 0 and step_j == 0:
                continue
            for distance in range(1, game.win_threshold):
                check_i = last_i + step_i * distance
                check_j = last_j + step_j * distance
                if (check_i < 0 or check_i >= game.height
                        or check_j < 0 or check_j >= game.width):
                    break
                if (game.field[check_i][check_j]
                        == game.field[last_i][last_j]):
                    captured[step_i + 1][step_j + 1] = distance
                else:
                    break

    return check_captured(last_i, last_j, game, captured)


def check_win_history(last_i, last_j, game):
    last_player_i = (len(game.history) - 1) % len(game.order)
    history_sorted = sorted(
        game.history[last_player_i::len(game.order)],
        key=lambda p: abs(p[0] - last_i) + abs(p[1] - last_j)
    )
    captured = [[0] * 3 for _ in range(3)]

    for turn in history_sorted:
        delta_i = turn[0] - last_i
        delta_j = turn[1] - last_j
        max_abs = max(abs(delta_i), abs(delta_j))
        if (abs(delta_i) == abs(delta_j) or 0 in (delta_j, delta_i)) \
                and max_abs != 0:
            step_i = delta_i // max_abs
            step_j = delta_j // max_abs
            if captured[step_i + 1][step_j + 1] + 1 == max_abs:
                captured[step_i + 1][step_j + 1] = max_abs

    return check_captured(last_i, last_j, game, captured)


def init_field(game):
    game.field = [[-1] * game.width for _ in range(game.height)]
    for i in range(len(game.history)):
        turn = game.history[i]
        game.field[turn[0]][turn[1]] = i % len(game.order)


def check_win(last_i, last_j, game):
    if game.field is None \
            and len(game.history) > 2 * min(game.width, game.height):
        init_field(game)

    if game.field is not None:
        return check_win_field(last_i, last_j, game)
    else:
        return check_win_history(last_i, last_j, game)


@lru_cache(maxsize=None)
def get_image_pattern(name):
    path = os.path.join(BASE_DIR, 'ticTacToe', 'picPatterns', name)
    with open(path, 'rb') as f:
        pattern = pickle.load(f)
    for row in pattern:
        for pix in row:
            pix.insert(0, pix[0])
            pix.insert(0, pix[0])
    return numpy.array(pattern, numpy.uint8)


@lru_cache
def generate_image_bytes(r, g, b, name):
    pattern = get_image_pattern(name).copy()

    pix_array = numpy.multiply(pattern, (r / 255, g / 255, b / 255, 1))
    pix_array = numpy.round(pix_array, 0).astype(numpy.uint8)
    result = Image.fromarray(pix_array)

    buffered = BytesIO()
    result.save(buffered, format="PNG")
    return buffered.getvalue()
