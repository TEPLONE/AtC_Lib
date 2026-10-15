from array import array
from typing import Sequence, Iterable, Tuple
class PrefixSumND:
    """
    N次元累積和（半開区間 [l, r) 仕様）
    ex.)   ruiseki = PrefixSumND((n,n,n), a, dtype="bigint")
           ruiseki.build()
           ans = ruiseki.sum([(lx,rx),(ly,ry),(lz,rz)])
    Maybe, bigint is fastest...
    dtype: 'int64' | 'float64' | 'bigint'
    - int64: array('q') 64-bit signed integer
    - float64: array('d') 64-bit float
    - bigint: Python int (arbitrary precision), internal buffer is list
    """
    _dtype_map = {
        'int64': {'typecode': 'q', 'cast': int, 'zero': 0, 'use_array': True},
        'float64': {'typecode': 'd', 'cast': float, 'zero': 0.0, 'use_array': True},
        'bigint': {'typecode': None, 'cast': int, 'zero': 0, 'use_array': False},
    }

    def __init__(self, shape: Sequence[int], data: Iterable = None, dtype: str = 'bigint'):
        self.shape = tuple(int(s) for s in shape)
        self.ndim = len(self.shape)
        if self.ndim == 0:
            raise ValueError("shape must have at least one dimension")
        self.size = 1
        for s in self.shape:
            if s <= 0:
                raise ValueError("shape must be positive")
            self.size *= s

        if dtype not in self._dtype_map:
            raise ValueError("unsupported dtype; choose 'int64', 'float64', or 'bigint'")
        self.dtype = dtype
        info = self._dtype_map[dtype]
        self._typecode = info['typecode']
        self._cast = info['cast']
        self._zero = info['zero']
        self._use_array = info['use_array']

        if self._use_array:
            self.buf = array(self._typecode, [self._zero]) * self.size
        else:
            # bigint: use Python list of ints
            self.buf = [self._zero] * self.size

        if data is not None:
            self._load_data(data)

        self.strides = self._calc_strides(self.shape)

    def _calc_strides(self, shape: Sequence[int]) -> Tuple[int, ...]:
        strides = [1] * len(shape)
        for i in range(len(shape)-2, -1, -1):
            strides[i] = strides[i+1] * shape[i+1]
        return tuple(strides)

    def _load_data(self, data: Iterable):
        flat = []
        def _flatten(x):
            if isinstance(x, (list, tuple)):
                for y in x:
                    _flatten(y)
            else:
                flat.append(self._cast(x))
        _flatten(data)
        if len(flat) != self.size:
            raise ValueError("data size mismatch")
        if self._use_array:
            self.buf = array(self._typecode, flat)
        else:
            # ensure Python ints
            self.buf = [int(v) for v in flat]

    def _index(self, coords: Sequence[int]) -> int:
        idx = 0
        for c, s in zip(coords, self.strides):
            idx += int(c) * s
        return idx

    def build(self):
        """各軸ごとに1次元累積和を行う（in-place）"""
        shape = self.shape
        strides = self.strides
        buf = self.buf
        ndim = self.ndim
        zero = self._zero

        for axis in range(ndim):
            step = strides[axis]
            block = 1
            for i in range(axis+1, ndim):
                block *= shape[i]
            repeat = self.size // (shape[axis] * block)
            for r in range(repeat):
                base = r * shape[axis] * block
                for off in range(block):
                    acc = zero
                    idx = base + off
                    for i in range(shape[axis]):
                        acc = acc + buf[idx]
                        buf[idx] = acc
                        idx += step

    def sum(self, ranges: Sequence[Tuple[int, int]]):
        """
        ex.) sum([(lx,rx),(ly,ry),(lz,rz)])
        ranges: sequence of (l, r) for each axis, 0 <= l <= r <= shape[axis]
        returns sum over indices where each axis in [l, r) (半開区間)
        """
        if len(ranges) != self.ndim:
            raise ValueError("ranges length mismatch")
        ls = [int(l) for l, _ in ranges]
        rs = [int(r) for _, r in ranges]
        total = self._zero

        for bits in range(1 << self.ndim):
            coords = []
            count_l = 0
            for d in range(self.ndim):
                if (bits >> d) & 1:
                    coords.append(ls[d])
                    count_l += 1
                else:
                    coords.append(rs[d])
            if any(c == 0 for c in coords):
                continue
            sign = -1 if (count_l % 2 == 1) else 1
            last_coords = [c - 1 for c in coords]
            idx = self._index(last_coords)
            total = total + sign * self.buf[idx]
        return total

    @classmethod
    def from_nested(cls, nested, dtype: str = 'bigint'):
        def shape_of(x):
            if isinstance(x, (list, tuple)):
                if not x:
                    return (0,)
                first = x[0]
                rest_shape = shape_of(first)
                return (len(x),) + rest_shape
            else:
                return ()
        shape = shape_of(nested)
        inst = cls(shape, nested, dtype=dtype)
        inst.strides = inst._calc_strides(inst.shape)
        inst.build()
        return inst
