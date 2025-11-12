"""
Rescale constellation star coordinates to fit within defined map dimensions.
"""

import json
from pathlib import Path

MAP_WIDTH = 700
MAP_HEIGHT = 500
SCALE = 3.0
MARGIN = 10

MAX_X = (MAP_WIDTH / SCALE) - MARGIN
MAX_Y = (MAP_HEIGHT / SCALE) - MARGIN


input_file = Path("data/constellations.json")
with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)


min_x = float("inf")
max_x = float("-inf")
min_y = float("inf")
max_y = float("-inf")

for constellation in data["constellations"]:
    for star in constellation["starts"]:
        x = star["coordenates"]["x"]
        y = star["coordenates"]["y"]
        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)

x_span = max_x - min_x if max_x > min_x else 1
y_span = max_y - min_y if max_y > min_y else 1
target_x_span = MAX_X - MARGIN
target_y_span = MAX_Y - MARGIN

scale_factor = min(target_x_span / x_span, target_y_span / y_span)


for constellation in data["constellations"]:
    for star in constellation["starts"]:
        old_x = star["coordenates"]["x"]
        old_y = star["coordenates"]["y"]

        norm_x = (old_x - min_x) / x_span if x_span > 0 else 0.5
        norm_y = (old_y - min_y) / y_span if y_span > 0 else 0.5

        new_x = MARGIN + (norm_x * target_x_span)
        new_y = MARGIN + (norm_y * target_y_span)

        star["coordenates"]["x"] = round(new_x, 1)
        star["coordenates"]["y"] = round(new_y, 1)


with open(input_file, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
