class HashItem:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __repr__(self):
        return f"{{{repr(self.key)}: {repr(self.value)}}}"
