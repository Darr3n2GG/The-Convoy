import random
from typing import NamedTuple

class Area(NamedTuple):
    width: int
    height: int

# Helper function to generate a random position in an area
def get_random_pos(area: Area) -> list[int]:
    x = random.randrange(0, area.width)
    y = random.randrange(0, area.height)
    return [x, y]

# Helper function to generate a new random position not in excluded positions
def generate_unique_pos(excluded_positions: list, area: Area) -> list[int]:
    pos = get_random_pos(area)
    
    # Keep generating a new position if it's in the excluded positions
    while pos in excluded_positions:
        pos = get_random_pos(area)
        
    return pos

# Returns a new list of random positions based on frame size, avoiding overlaps
def generate_non_overlapping_pos(area: Area, overlapping_body: list=None) -> list[int]:
    excluded_positions = []

    # If overlapping_body is provided, combine it with convoy_body
    if overlapping_body:
        excluded_positions.extend(overlapping_body)

    # Generate a position not in any excluded body
    return generate_unique_pos(excluded_positions, area)