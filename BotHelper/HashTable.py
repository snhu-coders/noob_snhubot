from .HashItem import HashItem

class HashTable:
    """
    Implements a hash table data structure. Keys must be strings, but values can be any object.
    Utilizes a chain traversal method for collisions using Python lists.

    Does not implement deletion of items.
    """

    def __init__(self, size=1000):        
        self.size = size
        self.collisions = 0
        self.items = 0
        self.slots = [None for _ in range(self.size)]

        self._keys = []

    def __setitem__(self, key, value):
        """
        Allows for "HashTable[key] = value" syntax for setting values
        """
        self.put(key, value)

    def __getitem__(self, key):
        """
        Allows for "HashTable[key]" syntax for returning values
        """
        return self.get(key)

    def __repr__(self):
        """
        Return the official string representation of the data structure
        """    
        return f"{{{', '.join([f'{repr(key)}: {repr(self.get(key))}' for key in self._keys])}}}"

    def __missing__(self, key):
        return None

    def __len__(self):
        return self.items

    def _hash(self, key) -> int:
        """
        Return the hashed value of the key
        """
        return sum([ord(c) for c in key]) % self.size

    def keys(self):
        """
        Returns the list of keys
        """
        return self._keys

    def values(self):
        """
        Returns a list of values
        """
        return [self.get(key) for key in self._keys]        

    def put(self, key, value):
        """
        Add item to Hash Table. Creates a new list at the index, 
        or appends item to existing list in case of collision
        """
        item = HashItem(key, value)
        index = self._hash(key)

        if self.slots[index]:
            self.slots[index].append(item)
            self.collisions += 1
        else:
            self.slots[index] = [item]

        self.items += 1
        self._keys.append(key)

    def get(self, key):
        """
        Locates index of hashed value, traverses index list and returns value of key, if it exists
        """
        # if type(key) is not str:
        #     raise TypeError()

        if key not in self.keys():
            raise KeyError(key)
        else:
            index = self._hash(key)

            # Traverse slot index and return item when found
            if self.slots[index]:
                for item in self.slots[index]:
                    if item.key == key:
                        return item.value
   
if __name__ == "__main__":
    from datetime import datetime
    startTime = datetime.now()

    ht = HashTable(10)
    ht.put("good", "eggs")
    ht.put("better", "ham")
    ht.put("best", "spam")
    ht.put("ad", "do not")
    ht["bc"] = "collide"

    print("Inserts: ", datetime.now() - startTime)

    keys = ("good", "better", "best", "worst", "ad", "bc")

    lookupTime = datetime.now()
    for key in keys:
        print(ht[key])
    
    print("Lookups: ", datetime.now() - lookupTime)
    print("Total: ", datetime.now() - startTime)

    print(ht.keys())
    print(repr(ht))
