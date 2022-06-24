class Trigger:
    def __init__(self, trigger: str, actor):
        self.trigger = trigger
        self.actor = actor

    def __call__(self, data):
        return self.actor(data)
