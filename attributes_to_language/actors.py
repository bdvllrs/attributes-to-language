import random


class WriterActor:
    def __init__(self, writers, data_key):
        self.writers = writers
        self.data_key = data_key

    def __call__(self, data):
        writer = random.choice(self.writers)
        x = data[self.data_key]
        if isinstance(x, (list, tuple)):
            return writer(*x)
        return writer(x)


class VariantActor:
    def __init__(self, variants):
        self.variants = variants

    def __call__(self, _):
        return random.choice(self.variants)
