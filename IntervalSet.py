import random
class IntervalSet:
    class Node:
        __slots__ = ("l", "r", "pri", "left", "right", "size", "total")

        def __init__(self, l, r):
            self.l = l
            self.r = r
            self.pri = random.getrandbits(64)
            self.left = None
            self.right = None
            self.size = 1
            self.total = r - l

    def __init__(self, intervals=None):
        self.root = None
        if intervals:
            for l, r in intervals:
                self.add(l, r)

    @staticmethod
    def _size(t):
        return t.size if t else 0

    @staticmethod
    def _total(t):
        return t.total if t else 0

    @classmethod
    def _update(cls, t):
        if t:
            t.size = 1 + cls._size(t.left) + cls._size(t.right)
            t.total = (
                t.r - t.l
                + cls._total(t.left)
                + cls._total(t.right)
            )
        return t

    @classmethod
    def _merge(cls, a, b):
        if not a:
            return b
        if not b:
            return a
        if a.pri > b.pri:
            a.right = cls._merge(a.right, b)
            return cls._update(a)
        b.left = cls._merge(a, b.left)
        return cls._update(b)

    @classmethod
    def _split(cls, t, key):
        if not t:
            return None, None
        if t.l < key:
            a, b = cls._split(t.right, key)
            t.right = a
            return cls._update(t), b
        a, b = cls._split(t.left, key)
        t.left = b
        return a, cls._update(t)

    @classmethod
    def _pop_min(cls, t):
        if not t.left:
            rest = t.right
            t.right = None
            cls._update(t)
            return t, rest
        node, t.left = cls._pop_min(t.left)
        return node, cls._update(t)

    @classmethod
    def _pop_max(cls, t):
        if not t.right:
            rest = t.left
            t.left = None
            cls._update(t)
            return t, rest
        node, t.right = cls._pop_max(t.right)
        return node, cls._update(t)

    @classmethod
    def _insert(cls, t, node):
        a, b = cls._split(t, node.l)
        return cls._merge(cls._merge(a, node), b)

    def add(self, l, r=None):
        if r is None:
            r = l + 1
        if l >= r:
            return

        a, b = self._split(self.root, l)
        node = None

        if a:
            p, a = self._pop_max(a)
            if p.r >= l:
                l = p.l
                r = max(r, p.r)
                node = p
            else:
                a = self._merge(a, p)

        b, c = self._split(b, r + 1)

        if b:
            p = b
            while p.right:
                p = p.right
            if p.r > r:
                r = p.r

        if node is None:
            node = self.Node(l, r)
        else:
            node.l = l
            node.r = r
            self._update(node)

        self.root = self._merge(self._merge(a, node), c)

    def discard(self, l, r=None):
        if r is None:
            r = l + 1
        if l >= r:
            return

        a, b = self._split(self.root, l)

        if a:
            p, a = self._pop_max(a)

            if p.r > l:
                old_r = p.r
                p.r = l
                self._update(p)
                a = self._merge(a, p)

                if old_r > r:
                    q = self.Node(r, old_r)
                    self.root = self._merge(a, self._merge(q, b))
                    return
            else:
                a = self._merge(a, p)

        b, c = self._split(b, r)

        if b:
            p, b = self._pop_max(b)

            if p.r > r:
                p.l = r
                self._update(p)
                c = self._merge(p, c)

        self.root = self._merge(a, c)

    def contains(self, x):
        t = self.root
        while t:
            if x < t.l:
                t = t.left
            elif x >= t.r:
                t = t.right
            else:
                return True
        return False

    def __contains__(self, x):
        return self.contains(x)

    def mex(self, x=0):
        t = self.root
        ans = x

        while t:
            if t.r <= ans:
                t = t.right
            elif t.l > ans:
                t = t.left
            else:
                ans = t.r
                t = t.right

        return ans

    def __len__(self):
        return self._total(self.root)

    @property
    def interval_count(self):
        return self._size(self.root)

    def __iter__(self):
        stack = []
        t = self.root

        while stack or t:
            while t:
                stack.append(t)
                t = t.left
            t = stack.pop()
            yield t.l, t.r
            t = t.right

    def __repr__(self):
        return f"IntervalSet({list(self)!r})"

    def clear(self):
        self.root = None

    def __getitem__(self, i):
        if i < 0:
            i += self.interval_count
        if not 0 <= i < self.interval_count:
            raise IndexError("IntervalSet index out of range")

        t = self.root
        while t:
            left_size = self._size(t.left)

            if i < left_size:
                t = t.left
            elif i == left_size:
                return (t.l, t.r)
            else:
                i -= left_size + 1
                t = t.right

    def discard_many_sorted(self, intervals):
        cuts = []

        for l, r in intervals:
            if l >= r:
                continue

            if cuts and l <= cuts[-1][1]:
                if r > cuts[-1][1]:
                    cuts[-1][1] = r
            else:
                cuts.append([l, r])

        if not cuts or self.root is None:
            return

        out = []
        j = 0
        m = len(cuts)
        changed = False

        for L, R in self:
            x = L

            while j < m and cuts[j][1] <= x:
                j += 1

            while j < m and cuts[j][0] < R:
                changed = True
                a, b = cuts[j]

                if a > x:
                    out.append((x, a))

                if b >= R:
                    x = R
                    if b == R:
                        j += 1
                    break

                x = b
                j += 1

            if x < R:
                out.append((x, R))

        if not changed:
            return

        stack = []

        for l, r in out:
            node = self.Node(l, r)
            last = None

            while stack and stack[-1].pri <= node.pri:
                last = stack.pop()

            node.left = last

            if stack:
                stack[-1].right = node

            stack.append(node)

        root = stack[0] if stack else None

        if root:
            order = []
            todo = [root]

            while todo:
                node = todo.pop()
                order.append(node)

                if node.left:
                    todo.append(node.left)
                if node.right:
                    todo.append(node.right)

            for node in reversed(order):
                self._update(node)

        self.root = root

    def add_many_sorted(self, intervals):
        adds = []

        for l, r in intervals:
            if l >= r:
                continue

            if adds and l <= adds[-1][1]:
                if r > adds[-1][1]:
                    adds[-1][1] = r
            else:
                adds.append([l, r])

        if not adds:
            return

        old = iter(self)
        cur = next(old, None)
        i = 0
        merged = []

        while cur is not None or i < len(adds):
            if i == len(adds) or (
                cur is not None and cur[0] <= adds[i][0]
            ):
                l, r = cur
                cur = next(old, None)
            else:
                l, r = adds[i]
                i += 1

            if merged and l <= merged[-1][1]:
                if r > merged[-1][1]:
                    merged[-1][1] = r
            else:
                merged.append([l, r])

        stack = []

        for l, r in merged:
            node = self.Node(l, r)
            last = None

            while stack and stack[-1].pri <= node.pri:
                last = stack.pop()

            node.left = last

            if stack:
                stack[-1].right = node

            stack.append(node)

        root = stack[0] if stack else None

        if root:
            order = []
            todo = [root]

            while todo:
                node = todo.pop()
                order.append(node)

                if node.left:
                    todo.append(node.left)
                if node.right:
                    todo.append(node.right)

            for node in reversed(order):
                self._update(node)

        self.root = root