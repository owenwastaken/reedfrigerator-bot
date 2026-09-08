import heapq
import time


class TTLDict:
    """A Python Dictionary that supports timed expiry of entries.

    ```
    my_dict = ttldict.TTLDict()
    my_dict.set("key", "value", 5)

    # prints "value"
    print(my_dict.get("value"))

    time.sleep(10)

    # prints None
    print(my_dict.get("value"))
    ```

    """

    def _garbage_collect(func):
        """Decorator that causes expired keys to be evicted before the target method is called"""

        def pre_gc(self, *args, **kwargs):
            self.gc()
            return func(self, *args, **kwargs)

        return pre_gc

    def __init__(self, gettimefunc=time.time):
        """This class maintains two structures: The first `__dict` is a dictionary that contains
        all the kv-pairs in the TTL dict. The second `__ttls` is a heap ordered by expiry unix
        timestamp.
        Before any elements are accessed, expired keys are garbage collected.
        """
        self.__dict = {}
        self.__gettime = gettimefunc
        self.__ttls = []

    def __setitem__(self, key, value):
        self.set(key, value)

    @_garbage_collect
    def __getitem__(self, key):
        return self.__dict[key]

    @_garbage_collect
    def __len__(self):
        return len(self.__dict)

    def set(self, key, value, ttl_seconds=float("INF")):
        expire_ts = self.__gettime() + ttl_seconds
        entry = (expire_ts, key)

        # If the client is updating a key then we need to update
        # its TTL as well. Unfortunately this means perturbing the
        # heap property which means we have to call an O(n) heapify again.
        if key in self.__dict:
            for i, e in enumerate(self.__ttls):
                k = e[1]
                if k == key:
                    del self.__ttls[i]
                    self.__ttls.append(entry)
                    break
            heapq.heapify(self.__ttls)  # The O(n) heapify
        else:
            heapq.heappush(self.__ttls, entry)

        self.__dict[key] = value

    @_garbage_collect
    def get(self, key):
        return self.__dict.get(key)

    @_garbage_collect
    def as_dict(self):
        return dict(self.__dict)

    def gc(self):
        current_ts = self.__gettime()

        while len(self.__ttls) > 0:
            expire_ts, key = self.__ttls[0]
            if expire_ts > current_ts:
                break

            heapq.heappop(self.__ttls)
            del self.__dict[key]
