import random
from typing import Dict

import numpy as np

from attributes_to_language.utils import COLORS_LARGE_SET, get_closest_key, COLORS_SPARSE


class Writer:
    """
    Writer instances generate the text associated to a specific value of an attribute.
    They can have different ways of describing the same element. This is defined by the "label_type" property.
    """

    def __init__(self, caption=None, variants=None):
        self.caption = caption if caption is not None else "{val}"
        self.variants = variants if variants is not None else {}

    def __call__(self, val):
        variants = dict()
        for k, choices in self.variants.items():
            variants[k] = random.choice(choices)

        val = str(val).format(**variants)
        text = self.caption.format(val=val, **variants)
        return text


class OptionsWriter(Writer):
    def __init__(self, choices, caption=None, variants=None):
        super(OptionsWriter, self).__init__(caption, variants)
        self.choices = choices

    def __call__(self, val):
        assert val in self.choices, f"{self.choices} does not contain options for {val}"
        selected_option = random.choice(self.choices[val])
        return super(OptionsWriter, self).__call__(selected_option)


class QuantizedWriter(Writer):
    def __init__(self, quantized_values, caption=None, variants=None, labels=None, norm="2"):
        super(QuantizedWriter, self).__init__(caption, variants)

        self.quantized_values = quantized_values
        self.labels = dict() if labels is None else labels
        self.norm = norm

    def __call__(self, *val):
        quantized_val = get_closest_key(self.quantized_values, val, self.norm)
        text = self.labels[quantized_val]
        if type(text) is list:
            text = random.choice(text)
        return super(QuantizedWriter, self).__call__(text)


class BinsWriter(Writer):
    def __init__(self, bins, caption=None, variants=None, labels=None):
        super(BinsWriter, self).__init__(caption, variants)
        self.bins = bins
        self.labels = dict() if labels is None else labels

    def __call__(self, val):
        index = np.digitize([val], self.bins)[0]
        text = self.labels[index]
        if type(text) is list:
            text = random.choice(text)
        return super(BinsWriter, self).__call__(text)


class Bins2dWriter(Writer):
    def __init__(self, bins, caption=None, variants=None, labels=None):
        super(Bins2dWriter, self).__init__(caption, variants)
        self.bins = bins
        self.labels = dict() if labels is None else labels

    def __call__(self, *val):
        label = self.labels
        for k in range(self.bins.shape[0]):
            bins = self.bins[k]
            index = np.digitize([val[k]], bins)[0]
            label = label[index]
        text = label
        if type(text) is list:
            text = random.choice(text)
        return super(Bins2dWriter, self).__call__(text)


class ContinuousAngleWriter(Writer):
    def __init__(self, caption=None, variants=None, sampling=5):
        super(ContinuousAngleWriter, self).__init__(caption, variants)
        self.sampling = sampling

    def __call__(self, angle):
        """
        Args:
            angle: Angle of the object in radians
        """
        if angle < 0:
            angle = 2 * np.pi + angle
        # round to every 5 degrees and set in degrees
        deg = int(self.sampling * round(angle * 360 / (2 * np.pi) / self.sampling)) % 360
        return super(ContinuousAngleWriter, self).__call__(deg)
