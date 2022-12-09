import random

import re


class Composer:
    def __init__(self, script_structures, available_writers, variants=None, modifiers=None):
        """
        Args:
            script_structures: str of the script where attributes can be replaced by "{attr_name}" and possible variants
                by "{variant_name}".
            available_writers: Dict of list of writers for the attributes. The key of the dict corresponds to the attribute name
                and the value is a list of type "Writer".
            variants: dict where the keys are the {tokens} in the script and values are list of possible values to chose
                from.
            modifiers: list of transformation function to apply to the script structure before variants and
                attributes are set.
        """
        self.script_structures = script_structures
        self.writers = available_writers
        self.variants = variants if variants is not None else dict()
        self.modifiers = modifiers if modifiers is not None else dict()

    def get_attribute(self, name, value):
        writer = random.choice(self.writers[name])
        if not isinstance(value, (list, tuple)):
            value = (value,)
        return writer(*value)

    def chose_variant(self, name, attributes):
        variant = random.choice(self.variants[name])
        if callable(variant):
            return variant(attributes)
        return variant

    def chose_element(self, attributes=None, name=None):
        # Get value from writers if attribute
        if attributes is not None and name is not None and name in self.writers.keys() and name in attributes.keys():
            return attributes[name]

        if name is not None:
            return self.chose_variant(name, attributes)

        variants = dict()
        for k, choices in self.variants.items():
            variants[k] = self.chose_variant(k, choices)
        return variants

    def get_variant(self, attributes, caption):
        regex = r"\{([^\}]+)\}"
        updates = {}
        names = list(map(lambda x: x, re.findall(regex, caption)))
        for k, name in enumerate(names):
            if k >= 1 and names[k - 1] in attributes.keys():
                attributes['_prev'] = names[k - 1]
            if k < len(names) - 1 and names[k + 1] in attributes.keys():
                attributes['_next'] = names[k + 1]
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
        # Execute script_transform
        if self.modifiers is not None:
            for modifier in self.modifiers:
                selected_structure = modifier(selected_structure)
        # Get attributes
        defined_attr = dict()
        for name, attr in attributes.items():
            defined_attr[name] = self.get_attribute(name, attr)
        # Fill variants and attributes
        final_caption = self.get_variant(defined_attr, selected_structure).strip()
        # remove multiple spaces and spaces in front of "."
        return re.sub(' +', ' ', final_caption).replace(" .", ".")
