import random

import re


class Composer:
    def __init__(self, script_structures, variants, available_writers, modifiers=None):
        """
        Args:
            script_structures:
            variants:
            available_writers: Dict of list of writers for the attributes. The key of the dict corresponds to the attribute name
                and the value is a list of type "Writer".
        """
        self.script_structures = script_structures
        self.variants = variants
        self.writers = available_writers
        self.modifiers = modifiers

    def __call__(self, attributes):
        """
        Compose one sentence from a dict of attributes
        Args:
            attributes: Dictionary where a key is an attribute name and the value is the value of the attribute that
                will be provided to the associated writer.

        Returns: The composed sentence.
        """
        # Select one of the templates
        selected_structure = random.choice(self.script_structures)
        # Perform modifiers
        if self.modifiers is not None:
            for modifier in self.modifiers:
                selected_structure = modifier(selected_structure)
        # Decide which variants will be used
        variants = dict()
        for k, choices in self.variants.items():
            variants[k] = random.choice(choices)
        # Select a writer for each attribute and generate the str.
        written_attrs = dict()
        for attr_name, attr in attributes.items():
            writer = random.choice(self.writers[attr_name])
            if isinstance(attr, (list, tuple)):
                written_attrs[attr_name] = writer(*attr).format(**variants)
            else:
                written_attrs[attr_name] = writer(attr).format(**variants)
        # Create final caption
        final_caption = selected_structure.format(**written_attrs, **variants).strip()
        # remove multiple spaces and spaces in front of "."
        return re.sub(' +', ' ', final_caption).replace(" .", ".")
