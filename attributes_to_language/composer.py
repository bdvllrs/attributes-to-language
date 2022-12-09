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

    def chose_element(self, attributes=None, name=None):
        # Get value from writers if attribute
        if attributes is not None and name is not None and name in self.writers.keys() and name in attributes.keys():
            writer = random.choice(self.writers[name])
            attr = attributes[name]
            if not isinstance(attr, (list, tuple)):
                attr = (attr,)
            return writer(*attr)

        if name is not None:
            return random.choice(self.variants[name])

        variants = dict()
        for k, choices in self.variants.items():
            variants[k] = random.choice(choices)
        return variants

    def get_variant(self, attributes, caption):
        regex = r"\{([^\}]+)\}"
        updates = {}
        for match in re.finditer(regex, caption):
            name = match.group(1)
            updates[name] = self.chose_element(attributes, name)

        if not len(updates):
            return caption

        caption = caption.format(**updates)
        return self.get_variant(attributes, caption)

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
        # Execute modifiers
        if self.modifiers is not None:
            for modifier in self.modifiers:
                selected_structure = modifier(selected_structure)
        # Fill variants and attributes
        final_caption = self.get_variant(attributes, selected_structure).strip()
        # remove multiple spaces and spaces in front of "."
        return re.sub(' +', ' ', final_caption).replace(" .", ".")
