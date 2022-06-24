import random

import re


class Composer:
    def __init__(self, script_structures, triggers):
        """
        Args:
            script_structures:
            triggers: List of triggers that will be called when a certain key is met in the structure
        """
        self.script_structures = script_structures
        self.triggers = triggers

    def __call__(self, data):
        """
        Compose one sentence from a dict of data
        Args:
            data: Dictionary where a key is an attribute name and the value is the value of the attribute that
                will be provided to the associated writer.

        Returns: The composed sentence.
        """
        # Select one of the templates
        selected_structure = random.choice(self.script_structures)
        regex = r"{(.+?)}"
        match = re.search(regex, selected_structure)
        while match:
            key = match.group(1)
            has_triggered = False
            for trigger in self.triggers:
                if trigger.trigger == key:
                    selected_structure = selected_structure.replace(match.group(), trigger(data))
                    has_triggered = True
                    break
            match = re.search(regex, selected_structure) if has_triggered else False
        return re.sub(' +', ' ', selected_structure).replace(" .", ".")
