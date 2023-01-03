import random
from typing import Dict

import numpy as np

from attributes_to_language.utils import COLORS_LARGE_SET, get_closest_key, COLORS_SPARSE


def choose_text(text, choices):
    if type(text) is list:
        if "val" not in choices:
            choices['val'] = random.randint(0, len(text) - 1)
        text = text[choices['val']]
    return text, choices


class Writer:
    """
    Writer instances generate the text associated to a specific value of an attribute.
    They can have different ways of describing the same element. This is defined by the "label_type" property.
    """

    def __init__(self, caption=None, variants=None):
        self.caption = caption if caption is not None else "{val}"
        self.variants = variants if variants is not None else {}

    def __call__(self, val, choices=None):
        variants = dict()
        if choices is None:
            choices = dict()
        for k, possible_variants in self.variants.items():
            if k not in choices:
                choices[k] = random.randint(0, len(possible_variants) - 1)
            variants[k] = possible_variants[choices[k]]

        val = str(val).format(**variants)
        text = self.caption.format(val=val, **variants)
        return text, choices


class OptionsWriter(Writer):
    def __init__(self, choices, caption=None, variants=None):
        super(OptionsWriter, self).__init__(caption, variants)
        self.choices = choices

    def __call__(self, val, choices=None):
        assert val in self.choices, f"{self.choices} does not contain options for {val}"
        if choices is None:
            choices = dict()
        if "val" not in choices:
            choices["val"] = random.randint(0, len(self.choices[val]) - 1)
        selected_option = self.choices[val][choices['val']]
        text, variant_choices = super(OptionsWriter, self).__call__(selected_option, choices)
        return text, {**choices, **variant_choices}


class QuantizedWriter(Writer):
    def __init__(self, quantized_values, caption=None, variants=None, labels=None, norm="2"):
        super(QuantizedWriter, self).__init__(caption, variants)

        self.quantized_values = quantized_values
        self.labels = dict() if labels is None else labels
        self.norm = norm

    def __call__(self, *val, choices=None):
        if choices is None:
            choices = dict()
        quantized_val = get_closest_key(self.quantized_values, val, self.norm)
        text = self.labels[quantized_val]
        text, choices = choose_text(text, choices)
        text, variant_choices = super(QuantizedWriter, self).__call__(text, choices)
        return text, {**choices, **variant_choices}


class BinsWriter(Writer):
    def __init__(self, bins, caption=None, variants=None, labels=None):
        super(BinsWriter, self).__init__(caption, variants)
        self.bins = bins
        self.labels = dict() if labels is None else labels

    def __call__(self, val, choices=None):
        if choices is None:
            choices = dict()
        index = np.digitize([val], self.bins)[0]
        text = self.labels[index]
        text, choices = choose_text(text, choices)
        text, variant_choices = super(BinsWriter, self).__call__(text, choices)
        return text, {**choices, **variant_choices}


class Bins2dWriter(Writer):
    def __init__(self, bins, caption=None, variants=None, labels=None):
        super(Bins2dWriter, self).__init__(caption, variants)
        self.bins = bins
        self.labels = dict() if labels is None else labels

    def __call__(self, *val, choices=None):
        if choices is None:
            choices = dict()
        label = self.labels
        for k in range(self.bins.shape[0]):
            bins = self.bins[k]
            index = np.digitize([val[k]], bins)[0]
            label = label[index]
        text, choices = choose_text(label, choices)
        text, variant_choices = super(Bins2dWriter, self).__call__(text, choices)
        return text, {**choices, **variant_choices}


class ContinuousAngleWriter(Writer):
    def __init__(self, caption=None, variants=None, sampling=5):
        super(ContinuousAngleWriter, self).__init__(caption, variants)
        self.sampling = sampling

    def __call__(self, angle, choices=None):
        """
        Args:
            angle: Angle of the object in radians
        """
        if angle < 0:
            angle = 2 * np.pi + angle
        # round to every 5 degrees and set in degrees
        deg = int(self.sampling * round(angle * 360 / (2 * np.pi) / self.sampling)) % 360
        return super(ContinuousAngleWriter, self).__call__(deg, choices)
