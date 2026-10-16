from atcoder.segtree import SegTree
from math import gcd, inf

class _RangeSegTreeView:
    __slots__ = ("_owner", "_name")

    def __init__(self, owner, name):
        self._owner = owner
        self._name = name

    @property
    def n(self):
        return self._owner.n

    def __len__(self):
        return self._owner.n

    def set(self, i, x):
        self._owner.set(i, x)

    def get(self, i):
        return self._owner.get(i)

    def prod(self, l, r):
        return self._owner._get_tree(self._name).prod(l, r)

    def all_prod(self):
        return self._owner._get_tree(self._name).all_prod()

    def max_right(self, l, f):
        return self._owner._get_tree(self._name).max_right(l, f)

    def min_left(self, r, f):
        return self._owner._get_tree(self._name).min_left(r, f)

    def __getitem__(self, i):
        return self.get(i)

    def __setitem__(self, i, x):
        self.set(i, x)


class RangeSegTree:
    """
    Initialize: 
        seg = RangeSegTree(a)
    Prod:
        ans = seg.sum.prod(l,r)
        ans2 = seg.max.prod(l,r)  etc.
    """
    def __init__(self, a):
        self._data = list(a)
        self.n = len(self._data)
        self._trees = {}
        self._views = {}
        self._specs = self._make_specs()

    @staticmethod
    def _make_specs():

        def min_index_op(x, y):
            if x[0] < y[0]:
                return x
            if y[0] < x[0]:
                return y
            return x if x[1] <= y[1] else y

        def max_index_op(x, y):
            if x[0] > y[0]:
                return x
            if y[0] > x[0]:
                return y
            return x if x[1] <= y[1] else y

        def min_count_op(x, y):
            if x[0] < y[0]:
                return x
            if y[0] < x[0]:
                return y
            return (x[0], x[1] + y[1])

        def max_count_op(x, y):
            if x[0] > y[0]:
                return x
            if y[0] > x[0]:
                return y
            return (x[0], x[1] + y[1])

        def minmax_op(x, y):
            return (min(x[0], y[0]), max(x[1], y[1]))

        def sum_min_prefix_op(x, y):
            return (x[0] + y[0], min(x[1], x[0] + y[1]))

        def max2_op(x, y):
            values = [v for v in x + y if v is not None]
            values.sort(reverse=True)

            res = []
            for v in values:
                if not res or v != res[-1]:
                    res.append(v)
                if len(res) == 2:
                    break

            return (
                res[0] if res else None,
                res[1] if len(res) > 1 else None
            )

        def min2_op(x, y):
            values = [v for v in x + y if v is not None]
            values.sort()

            res = []
            for v in values:
                if not res or v != res[-1]:
                    res.append(v)
                if len(res) == 2:
                    break

            return (
                res[0] if res else None,
                res[1] if len(res) > 1 else None
            )

        def run_op(x, y):
            if x[0] == 0:
                return y
            if y[0] == 0:
                return x

            same = x[2] == y[1]

            length = x[0] + y[0]

            prefix = (
                x[3] + y[3]
                if same and x[3] == x[0]
                else x[3]
            )

            suffix = (
                y[4] + x[4]
                if same and y[4] == y[0]
                else y[4]
            )

            best = max(
                x[5],
                y[5],
                x[4] + y[3] if same else 0
            )

            return (
                length,
                x[1],
                y[2],
                prefix,
                suffix,
                best
            )

        def max_subarray_op(x, y):
            if x[0] == 0:
                return y
            if y[0] == 0:
                return x

            return (
                x[0] + y[0],
                x[1] + y[1],
                max(x[2], x[1] + y[2]),
                max(y[3], y[1] + x[3]),
                max(x[4], y[4], x[3] + y[2])
            )

        return {
            "sum": (
                lambda x, i: x,
                lambda x, y: x + y,
                0
            ),

            "min": (
                lambda x, i: x,
                min,
                inf
            ),

            "max": (
                lambda x, i: x,
                max,
                -inf
            ),

            "gcd": (
                lambda x, i: abs(x),
                lambda x, y: gcd(x, y),
                0
            ),

            "min_index": (
                lambda x, i: (x, i),
                min_index_op,
                (inf, inf)
            ),

            "max_index": (
                lambda x, i: (x, i),
                max_index_op,
                (-inf, inf)
            ),

            "min_count": (
                lambda x, i: (x, 1),
                min_count_op,
                (inf, 0)
            ),

            "max_count": (
                lambda x, i: (x, 1),
                max_count_op,
                (-inf, 0)
            ),

            "minmax": (
                lambda x, i: (x, x),
                minmax_op,
                (inf, -inf)
            ),

            "sum_min_prefix": (
                lambda x, i: (x, min(0, x)),
                sum_min_prefix_op,
                (0, 0)
            ),

            "max2": (
                lambda x, i: (x, None),
                max2_op,
                (None, None)
            ),

            "min2": (
                lambda x, i: (x, None),
                min2_op,
                (None, None)
            ),

            "run": (
                lambda x, i: (1, x, x, 1, 1, 1),
                run_op,
                (0, None, None, 0, 0, 0)
            ),

            "max_subarray": (
                lambda x, i: (1, x, x, x, x),
                max_subarray_op,
                (0, 0, -inf, -inf, -inf)
            )
        }

    def _normalize_index(self, i):
        if not isinstance(i, int):
            raise TypeError("index must be an integer")

        if i < 0:
            i += self.n

        if not 0 <= i < self.n:
            raise IndexError("segment tree index out of range")

        return i

    def _get_tree(self, name):
        if name not in self._trees:
            lift, op, e = self._specs[name]

            v = [
                lift(x, i)
                for i, x in enumerate(self._data)
            ]

            self._trees[name] = SegTree(op, e, v)

        return self._trees[name]

    def set(self, i, x):
        i = self._normalize_index(i)
        self._data[i] = x

        for name, tree in self._trees.items():
            lift, _, _ = self._specs[name]
            tree.set(i, lift(x, i))

    def get(self, i):
        return self._data[self._normalize_index(i)]

    def __getitem__(self, i):
        return self.get(i)

    def __setitem__(self, i, x):
        self.set(i, x)

    def __len__(self):
        return self.n

    def _get_view(self, name):
        if name not in self._views:
            self._views[name] = _RangeSegTreeView(self, name)
        return self._views[name]

    @property
    def sum(self) -> _RangeSegTreeView:
        """RangeSumSegTree"""
        return self._get_view("sum")

    @property
    def min(self) -> _RangeSegTreeView:
        """RangeMinSegTree"""
        return self._get_view("min")

    @property
    def max(self) -> _RangeSegTreeView:
        """RangeMaxSegTree"""
        return self._get_view("max")

    @property
    def gcd(self) -> _RangeSegTreeView:
        """RangeGCDSegTree"""
        return self._get_view("gcd")

    @property
    def min_index(self) -> _RangeSegTreeView:
        """
        RangeMin&IdxSegTree
        return (min, idx(The leftmost))
        """
        return self._get_view("min_index")

    @property
    def max_index(self) -> _RangeSegTreeView:
        """
        RangeMax&IdxSegTree
        return (max, idx(The leftmost))
        """
        return self._get_view("max_index")

    @property
    def min_count(self) -> _RangeSegTreeView:
        """
        RangeMin&CountSegTree
        return (min, count)
        """
        return self._get_view("min_count")

    @property
    def max_count(self) -> _RangeSegTreeView:
        """
        RangeMax&CountSegTree
        return (max, count)
        """
        return self._get_view("max_count")

    @property
    def minmax(self) -> _RangeSegTreeView:
        """
        RangeMin&MaxSegTree
        return (min, max)
        """
        return self._get_view("minmax")

    @property
    def sum_min_prefix(self) -> _RangeSegTreeView:
        """
        RangeSum&MinprefixSegTree
        return (sum, minprefix)
        """
        return self._get_view("sum_min_prefix")

    @property
    def max2(self) -> _RangeSegTreeView:
        """
        RangeMax&Max2SegTree
        return (max, max2th)
        """
        return self._get_view("max2")

    @property
    def min2(self) -> _RangeSegTreeView:
        """
        RangeMin&Min2SegTree
        return (min, min2th)
        """
        return self._get_view("min2")

    @property
    def run(self) -> _RangeSegTreeView:
        """
        同じ値が連続する最長区間
        return (len, val_leftmost, val_rightmost, len_prefix, len_suffix, len_longest)
        """
        return self._get_view("run")

    @property
    def max_subarray(self) -> _RangeSegTreeView:
        """
        最大部分配列和
        return (len, sum, max_prefixsum, max_suffixsum, max_subarray)
        """
        return self._get_view("max_subarray")

    def __getattr__(self, name):
        specs = self.__dict__.get("_specs", {})
        if name in specs:
            return self._get_view(name)
        raise AttributeError(
            f"{type(self).__name__!r} object has no attribute {name!r}"
        )
