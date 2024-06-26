import random
from collections.abc import Callable, Sequence
from dataclasses import dataclass
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


def parse_groups(structure: str) -> list[str]:
    groups: list[str] = []
    is_in_group = False
    cur_group: str = ""
    for letter in structure:
        if letter == "<" and not is_in_group:
            is_in_group = True
            cur_group = "<"
        if letter == ">" and is_in_group:
            is_in_group = False
            assert cur_group is not None
            cur_group += ">"
            groups.append(cur_group)
            cur_group = ""
        if letter != "<" and is_in_group:
            assert cur_group is not None
            cur_group += letter
    return groups


def parse_tokens(structure: str) -> list[str]:
    tokens: list[str] = []
    is_in_token = False
    cur_token: str = ""
    for letter in structure:
        if letter == "{" and not is_in_token:
            is_in_token = True
            cur_token = ""
        if letter == "}" and is_in_token:
            is_in_token = False
            assert cur_token is not None
            tokens.append(cur_token)
            cur_token = ""
        if letter != "{" and is_in_token:
            assert cur_token is not None
            cur_token += letter
    return tokens


def remove_extra_spaces(text: str) -> str:
    return " ".join(text.split())


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
        self.groups: list[list[str]] = [parse_groups(s) for s in self.script_structures]

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
        self,
        attributes: ComputedAttributeT,
        caption: str,
        choices: ChoicesT,
    ) -> str:
        tokens = parse_tokens(caption)
        updates: dict[str, str] = {}
        for k, token in enumerate(tokens):
            if k >= 1 and tokens[k - 1] in attributes:
                attributes["_prev"] = tokens[k - 1]
            if k < len(tokens) - 1 and tokens[k + 1] in attributes:
                attributes["_next"] = tokens[k + 1]
            updates[token] = self.chose_element(attributes, token, choices)

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
        assert "structure" in choices
        struct_id = choices["structure"]
        original_groups = self.groups[struct_id]
        # Execute script_transform
        if self.modifiers is not None:
            for modifier in self.modifiers:
                selected_structure = modifier(selected_structure)
        # Switch groups
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
        return remove_extra_spaces(final_caption).replace(" .", "."), choices
