import numpy as np

from attributes_to_language.composer import Composer
from writers import writers


def a_has_n(sentence):
    def aux(attributes):
        vowels = ["a", "e", "i", "o", "u"]
        if attributes[attributes["_next"]][0] in vowels:
            return sentence.format(**{"n?": "n"})
        return sentence.format(**{"n?": ""})

    return aux


if __name__ == '__main__':
    # Templates for the overall text. The items in {} can come from the associated key in the "variants" dict attributes
    # or from a kwargs given to the composer method.
    script_structures = [
        "{start} {size} {colorBefore} {shape}, <{located}{in_the} {location}>{link} <{rotation}>.",
        "{start} {color} {size} {shape}, {located} {in_the} {location}{link} {rotation}.",
        "{start} {size} {shape} in {color} color, {located} {in_the} {location}{link} {rotation}.",
        "{start} {size} {shape} in {color} color{link} {located} {in_the} {location} and {is?}{rotation}.",
        "{start} {size} {color} {shape}{link} {located} {in_the} {location} and {is?}{rotation}.",
        "{start} {color} {size} {shape}{link} {located} {in_the} {location} and {is?}{rotation}.",
    ]

    start_variant = ["A", "It is a", "This is a", "There is a",
                     "The image is a", "The image represents a", "The image contains a"]
    start_variant = [a_has_n(x + "{n?}") for x in start_variant] + ["A kind of"]

    # Elements in the list of each variant is randomly chosen.
    variants = {
        "start": start_variant,
        "colorBefore": ["{color}", "{color} colored"],
        "located": ["", "located "],
        "in_the": ["in the", "at the"],
        "link": [". It is", ", and is"],
        "is?": ["", "is "]
    }

    composer = Composer(script_structures, writers, variants)

    for k in range(5):
        print(composer({
            "shape": 2,
            "rotation": np.pi / 6,
            "color": (129, 76, 200),
            "size": 20,
            "location": (29, 8)
        }))
