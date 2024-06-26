import random
import re
from collections.abc import Callable, Sequence
from typing import Any, TypeVar

import numpy as np

from attributes_to_language.types import (
    AttributeT,
    Choices,
    ChoicesT,
    ComputedAttributeT,
    VariantsT,
)
from attributes_to_language.writers import Writer

_T = TypeVar("_T")


def choose_element(key: str, options: Sequence[_T], choices: ChoicesT | Choices) -> _T:
    if key not in choices:
        choices[key] = random.randint(0, len(options) - 1)
    choice = options[choices[key]]
    return choice


class Composer:
    def __init__(
        self,
        script_structures: Sequence[str],
        available_writers: dict[str, Sequence[Writer]],
        variants: VariantsT | None = None,
        modifiers: Sequence[Callable[[str], str]] | None = None,
    ):
        """
        Args:
            script_structures: str of the script where attributes can be replaced by
                "{attr_name}" and possible variants by "{variant_name}".
            available_writers: Dict of list of writers for the attributes. The key of
                the dict corresponds to the attribute name and the value is a list of
                type "Writer".
            variants: dict where the keys are the {tokens} in the script and values are
                list of possible values to chose from.
            modifiers: list of transformation function to apply to the script structure
                before variants and attributes are set.
        """
        self.script_structures = script_structures
        self.writers = available_writers
        self.variants = variants or {}
        self.modifiers = modifiers or {}

    def get_attribute(
        self, name: str, value: Any, choices: ChoicesT
    ) -> tuple[str, ChoicesT]:
        writer = choose_element("_writer", self.writers[name], choices)
        if not isinstance(value, list | tuple):
            value = (value,)
        return writer(*value, choices=choices)

    def chose_variant(
        self, name: str, attributes: ComputedAttributeT | None, choices: ChoicesT
    ) -> str:
        variant = choose_element(name, self.variants[name], choices)
        if callable(variant):
            return variant(attributes)
        return variant

    def chose_element(
        self,
        attributes: ComputedAttributeT,
        name: str,
        choices: ChoicesT | None = None,
    ) -> str:
        if choices is None:
            choices = dict()
        # Get value from writers if attribute
        if name in self.writers and name in attributes:
            return attributes[name]

        return self.chose_variant(name, attributes, choices)

    def get_variant(
        self, attributes: ComputedAttributeT, caption: str, choices: ChoicesT
    ) -> str:
        regex = r"\{([^\}]+)\}"  # text in between {}
        # FIXME: custom parser
        updates: dict[str, str] = {}
        names = list(map(lambda x: x, re.findall(regex, caption)))
        for k, name in enumerate(names):
            if k >= 1 and names[k - 1] in attributes:
                attributes["_prev"] = names[k - 1]
            if k < len(names) - 1 and names[k + 1] in attributes:
                attributes["_next"] = names[k + 1]
            updates[name] = self.chose_element(attributes, name, choices)

        if not len(updates):
            return caption

        caption = caption.format(**updates)
        return self.get_variant(attributes, caption, choices)

    def __call__(self, attributes: AttributeT, choices: Choices | None = None):
        """
        Compose one sentence from a dict of attributes
        Args:
            attributes: Dictionary where a key is an attribute name and the value is the value of the attribute that
                will be provided to the associated writer.

        Returns: The composed sentence.
        """
        if choices is None:
            choices = Choices()
        # Select one of the templates
        selected_structure = choose_element(
            "structure", self.script_structures, choices
        )
        # Execute script_transform
        if self.modifiers is not None:
            for modifier in self.modifiers:
                selected_structure = modifier(selected_structure)
        # Switch groups
        original_groups = re.findall(r"<[^>]+>", selected_structure)
        if "groups" not in choices:
            choices["groups"] = np.random.permutation(len(original_groups)).tolist()
        groups = [original_groups[x] for x in choices["groups"]]
        for original_group, group in zip(original_groups, groups, strict=False):
            selected_structure = selected_structure.replace(original_group, group[1:-1])
        # Get attributes
        defined_attr = dict()
        if "writers" not in choices:
            choices["writers"] = dict()
        for name, attr in attributes.items():
            if name not in choices["writers"]:
                choices["writers"][name] = dict()
            defined_attr[name], writer_choices = self.get_attribute(
                name, attr, choices["writers"][name]
            )
            choices["writers"][name].update(writer_choices)
        # Fill variants and attributes
        if "variants" not in choices:
            choices["variants"] = dict()
        final_caption = self.get_variant(
            defined_attr, selected_structure, choices["variants"]
        ).strip()
        # remove multiple spaces and spaces in front of "."
        return re.sub(" +", " ", final_caption).replace(" .", "."), choices
