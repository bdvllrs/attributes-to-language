import numpy as np

from attributes_to_language.actors import VariantActor, WriterActor
from attributes_to_language.composer import Composer
from attributes_to_language.trigger import Trigger
from writers import writers

if __name__ == '__main__':
    # Templates for the overall text. The items in {} can come from the associated key in the "variants" dict attributes
    # or from a kwargs given to the composer method.
    script_structures = [
        "{start} {size} {color} {shape}, {located} {in_the} {location}{link} {rotation}.",
        "{start} {color} {size} {shape}, {located} {in_the} {location}{link} {rotation}.",
        "{start} {size} {shape} in {color} color, {located} {in_the} {location}{link} {rotation}.",
        "{start} {size} {shape} in {color} color{link} {located} {in_the} {location} and {is?}{rotation}.",
        "{start} {size} {color} {shape}{link} {located} {in_the} {location} and {is?}{rotation}.",
        "{start} {color} {size} {shape}{link} {located} {in_the} {location} and {is?}{rotation}.",
    ]


    triggers = [
        Trigger("start", VariantActor(["A", "It is a", "A kind of", "This is a", "There is a",
                                       "The image is a", "The image represents a", "The image contains a"])),
        Trigger("located", VariantActor(["", "located"])),
        Trigger("in_the", VariantActor(["in the", "at the"])),
        Trigger("link", VariantActor([". It is", ", and is"])),
        Trigger("is?", VariantActor(["", "is "])),
        Trigger("shape", WriterActor(writers["shape"], "shape")),
        Trigger("rotation", WriterActor(writers["rotation"], "rotation")),
        Trigger("color", WriterActor(writers["color"], "color")),
        Trigger("size", WriterActor(writers["size"], "size")),
        Trigger("location", WriterActor(writers["location"], "location")),
    ]

    composer = Composer(script_structures, triggers)

    for k in range(5):
        print(composer({
            "shape": 2,
            "rotation": np.pi / 6,
            "color": (129, 76, 200),
            "size": 20,
            "location": (29, 8)
        }))
