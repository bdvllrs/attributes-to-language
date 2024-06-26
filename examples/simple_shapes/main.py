from collections.abc import Callable, Mapping

import numpy as np
from writers import writers

from attributes_to_language.composer import Composer
from attributes_to_language.types import Choices


def a_has_n(sentence: str) -> Callable[[Mapping[str, str]], str]:
    """
    This replaces {n?} in the sentence with either "n" if the following letter is a
    vowel, or nothing otherwise.
    """

    def aux(
        attributes: Mapping[str, str],
    ):  # the variant callable must receive an "attributes" parameter.
        vowels = ["a", "e", "i", "o", "u"]
        # the "_next" represent the name of the next token if it is an attribute token
        # and if it exists.
        # similarly, "_prev" represent the name of the previous token.
        if attributes[attributes["_next"]][0] in vowels:
            return sentence.replace("{n?}", "n")
        return sentence.replace("{n?}", "")

    return aux


if __name__ == "__main__":
    # Templates for the overall text. The items in {} can come from the associated key
    # in the "variants" dict attributes
    # or from a kwargs given to the composer method.
    script_structures = [
        # The < and > delimit groups. Groups are then randomly permuted.
        # For example "<hello> <world>" will yield either "hello world" or "world hello".
        # Groups can contain variant or attribute tokens.
        "{start} {size} {colorBefore} {shape}, <{located}{in_the} {location}>{link} <{rotation}>.",
        "{start} {color} {size} {shape}, {located} {in_the} {location}{link} {rotation}.",
        "{start} {size} {shape} in {color} color, {located} {in_the} {location}{link} {rotation}.",
        "{start} {size} {shape} in {color} color{link} {located} {in_the} {location} and {is?}{rotation}.",
        "{start} {size} {color} {shape}{link} {located} {in_the} {location} and {is?}{rotation}.",
        "{start} {color} {size} {shape}{link} {located} {in_the} {location} and {is?}{rotation}.",
    ]

    start_variant = [
        "A",
        "It is a",
        "This is a",
        "There is a",
        "The image is a",
        "The image represents a",
        "The image contains a",
    ]
    # Variants can be callable functions. In this case, the called function will receive a dictionary with the attributes
    # formatted by the writers.
    start_variant = [a_has_n(x + "{n?}") for x in start_variant] + ["A kind of"]

    # Elements in the list of each variant is randomly chosen.
    variants = {
        "start": start_variant,
        "colorBefore": ["{color}", "{color} colored"],
        "located": ["", "located "],
        "in_the": ["in the", "at the"],
        "link": [". It is", ", and is"],
        "is?": ["", "is "],
    }

    composer = Composer(script_structures, writers, variants)
    choices: Choices = {
        "structure": 0,
        "groups": [0, 1],
        "writers": {
            "shape": {"_writer": 0, "val": 1},
            "rotation": {"_writer": 2, "anti_clock": 0},
            "color": {"_writer": 0},
            "size": {"_writer": 0, "val": 0},
            "location": {
                "_writer": 0,
                "val": 1,
                "located": 1,
                "prefix": 1,
                "postfix": 0,
                "of_image": 1,
            },
        },
        "variants": {
            "start": 0,
            "colorBefore": 1,
            "located": 1,
            "in_the": 0,
            "link": 0,
        },
    }

    "A big slate blue colored triangle, located in the lower right. It is rotated 30 degrees."

    for _ in range(5):
        sentence, choices = composer(
            {
                "shape": 2,
                "rotation": np.pi / 6,
                "color": (129, 76, 200),
                "size": 20,
                "location": (29, 8),
            },
            choices,
        )
        print(sentence)
        print(choices)
