import random
from collections.abc import Mapping, Sequence
from typing import Any, Literal

import numpy as np

from attributes_to_language.types import ChoicesT, VariantsT
from attributes_to_language.utils import get_closest_key


def choose_text(text: Sequence[str] | str, choices: ChoicesT) -> str:
    if isinstance(text, str):
        choices["val"] = 0
        return text
    if "val" not in choices:
        choices["val"] = random.randint(0, len(text) - 1)
    text = text[choices["val"]]
    return text


class Writer:
    """
    Writer instances generate the text associated to a specific value of an attribute.
    They can have different ways of describing the same element. This is defined by the
    "label_type" property.
    """

    def __init__(self, caption: str | None = None, variants: VariantsT | None = None):
        self.caption = caption or "{val}"
        self.variants = variants or {}

    def add_variants(
        self, val: str, choices: ChoicesT | None = None
    ) -> tuple[str, ChoicesT]:
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

    def __call__(
        self, *val: Any, choices: ChoicesT | None = None
    ) -> tuple[str, ChoicesT]:
        raise NotImplementedError


class OptionsWriter(Writer):
    def __init__(
        self,
        choices: Mapping[Any, Sequence[str]],
        caption: str | None = None,
        variants: VariantsT | None = None,
    ):
        super().__init__(caption, variants)
        self.choices = choices

    def __call__(
        self, *val: Any, choices: ChoicesT | None = None
    ) -> tuple[str, ChoicesT]:
        assert len(val) == 1
        name = val[0]
        assert (
            name in self.choices
        ), f"{self.choices} does not contain options for {name}"
        if choices is None:
            choices = dict()
        if "name" not in choices:
            choices["name"] = random.randint(0, len(self.choices[name]) - 1)
        selected_option = self.choices[name][choices["name"]]
        text, variant_choices = self.add_variants(selected_option, choices)
        return text, {**choices, **variant_choices}


class QuantizedWriter(Writer):
    def __init__(
        self,
        quantized_values: np.ndarray,
        caption: str | None = None,
        variants: VariantsT | None = None,
        labels: Sequence[Sequence[str]] | Sequence[str] | None = None,
        norm: Literal["1", "2"] = "2",
    ):
        super().__init__(caption, variants)

        self.quantized_values = quantized_values
        self.labels = labels or []
        self.norm: Literal["1", "2"] = norm

    def __call__(
        self, *val: Any, choices: ChoicesT | None = None
    ) -> tuple[str, ChoicesT]:
        if choices is None:
            choices = dict()
        quantized_val = get_closest_key(self.quantized_values, val, self.norm).item()
        text = self.labels[quantized_val]
        text = choose_text(text, choices)
        text, variant_choices = self.add_variants(text, choices)
        return text, {**choices, **variant_choices}


class BinsWriter(Writer):
    def __init__(
        self,
        bins: np.ndarray,
        caption: str | None = None,
        variants: VariantsT | None = None,
        labels: Sequence[Sequence[str]] | Sequence[str] | None = None,
    ):
        super().__init__(caption, variants)
        self.bins = bins
        self.labels = labels or []

    def __call__(
        self, *val: Any, choices: ChoicesT | None = None
    ) -> tuple[str, ChoicesT]:
        assert len(val) == 1
        item = val[0]
        if choices is None:
            choices = dict()
        index = np.digitize([item], self.bins).item()
        text = self.labels[index]
        text = choose_text(text, choices)
        text, variant_choices = self.add_variants(text, choices)
        return text, {**choices, **variant_choices}


class Bins2dWriter(Writer):
    def __init__(
        self,
        bins,
        caption: str | None = None,
        variants: VariantsT | None = None,
        labels: Sequence[Sequence[Sequence[str]]]
        | Sequence[Sequence[str]]
        | None = None,
    ):
        super().__init__(caption, variants)
        self.bins = bins
        self.labels = labels or [[]]

    def __call__(
        self, *val: Any, choices: ChoicesT | None = None
    ) -> tuple[str, ChoicesT]:
        if choices is None:
            choices = dict()
        assert self.bins.shape[0] == 2
        index_0 = np.digitize([val[0]], self.bins[0]).item()
        index_1 = np.digitize([val[1]], self.bins[1]).item()
        label = self.labels[index_0][index_1]
        text = choose_text(label, choices)
        text, variant_choices = self.add_variants(text, choices)
        return text, {**choices, **variant_choices}


class ContinuousAngleWriter(Writer):
    def __init__(
        self,
        caption: str | None = None,
        variants: VariantsT | None = None,
        sampling: int = 5,
    ):
        super().__init__(caption, variants)
        self.sampling = sampling

    def __call__(
        self, *val: Any, choices: ChoicesT | None = None
    ) -> tuple[str, ChoicesT]:
        """
        Args:
            angle: Angle of the object in radians
        """
        assert len(val) == 1
        angle = val[0]
        if angle < 0:
            angle = 2 * np.pi + angle
        # round to every 5 degrees and set in degrees
        deg = (
            int(self.sampling * round(angle * 360 / (2 * np.pi) / self.sampling)) % 360
        )
        return self.add_variants(str(deg), choices)
