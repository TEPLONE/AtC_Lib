# PyPy向け高速 implicit treap (クラス版)
import sys
sys.setrecursionlimit(1 << 25)

class XorShift:
    def __init__(self, seed=71268726):
        self.x = seed or 2463534242
    def rand(self):
        x = self.x
        x ^= (x << 13) & 0xFFFFFFFFFFFFFFFF
        x ^= (x >> 7)
        x ^= (x << 17) & 0xFFFFFFFFFFFFFFFF
        self.x = x
        return x & 0x7FFFFFFF

class FastImplicitTreap:
    def __init__(self, seed=71268726):
        self.rng = XorShift(seed)
        # pool arrays; index 0 == null
        self.VAL = [0]
        self.PR  = [0]
        self.L   = [0]
        self.R   = [0]
        self.SZ  = [0]
        self.SUM = [0]
        self.MX  = [0]
        self.MN  = [0]
        self.REV = [False]
        self.HAS_SET = [False]
        self.SET_VAL = [0]
        self.MUL = [1]
        self.ADD = [0]
        self.root = 0

    def _new_node(self, v):
        idx = len(self.VAL)
        self.VAL.append(v)
        self.PR.append(self.rng.rand())
        self.L.append(0); self.R.append(0)
        self.SZ.append(1)
        self.SUM.append(v)
        self.MX.append(v); self.MN.append(v)
        self.REV.append(False)
        self.HAS_SET.append(False)
        self.SET_VAL.append(0)
        self.MUL.append(1); self.ADD.append(0)
        return idx

    def _size(self, i):
        return self.SZ[i] if i else 0

    def _pull(self, i):
        v = self.VAL[i]
        li = self.L[i]; ri = self.R[i]
        s = v
        mx = v; mn = v
        if li:
            s += self.SUM[li]
            lm = self.MX[li]; ln = self.MN[li]
            if lm > mx: mx = lm
            if ln < mn: mn = ln
        if ri:
            s += self.SUM[ri]
            rm = self.MX[ri]; rn = self.MN[ri]
            if rm > mx: mx = rm
            if rn < mn: mn = rn
        self.SZ[i] = 1 + (self.SZ[li] if li else 0) + (self.SZ[ri] if ri else 0)
        self.SUM[i] = s
        self.MX[i] = mx
        self.MN[i] = mn

    def _apply_set(self, i, x):
        if not i: return
        self.HAS_SET[i] = True
        self.SET_VAL[i] = x
        self.MUL[i] = 1; self.ADD[i] = 0
        self.VAL[i] = x
        self.SUM[i] = x * self.SZ[i]
        self.MX[i] = x; self.MN[i] = x

    def _apply_mul_add(self, i, mul, add):
        if not i: return
        if self.HAS_SET[i]:
            nv = self.SET_VAL[i] * mul + add
            self.SET_VAL[i] = nv
            self.VAL[i] = nv
            self.SUM[i] = nv * self.SZ[i]
            self.MX[i] = nv; self.MN[i] = nv
            return
        self.MUL[i] = self.MUL[i] * mul
        self.ADD[i] = self.ADD[i] * mul + add
        self.VAL[i] = self.VAL[i] * mul + add
        self.SUM[i] = self.SUM[i] * mul + add * self.SZ[i]
        self.MX[i] = self.MX[i] * mul + add
        self.MN[i] = self.MN[i] * mul + add
        if mul < 0:
            self.MX[i], self.MN[i] = self.MN[i], self.MX[i]

    def _apply_rev(self, i):
        if not i: return
        self.REV[i] = not self.REV[i]
        self.L[i], self.R[i] = self.R[i], self.L[i]

    def _push(self, i):
        if not i: return
        if self.HAS_SET[i]:
            sv = self.SET_VAL[i]
            li = self.L[i]; ri = self.R[i]
            if li: self._apply_set(li, sv)
            if ri: self._apply_set(ri, sv)
            self.HAS_SET[i] = False
        if self.MUL[i] != 1 or self.ADD[i] != 0:
            li = self.L[i]; ri = self.R[i]
            if li: self._apply_mul_add(li, self.MUL[i], self.ADD[i])
            if ri: self._apply_mul_add(ri, self.MUL[i], self.ADD[i])
            self.MUL[i] = 1; self.ADD[i] = 0
        if self.REV[i]:
            li = self.L[i]; ri = self.R[i]
            if li: self._apply_rev(li)
            if ri: self._apply_rev(ri)
            self.REV[i] = False

    def _split(self, t, k):
        if t == 0:
            return 0, 0
        self._push(t)
        lsz = self._size(self.L[t])
        if k <= lsz:
            a, b = self._split(self.L[t], k)
            self.L[t] = b
            self._pull(t)
            return a, t
        else:
            a, b = self._split(self.R[t], k - lsz - 1)
            self.R[t] = a
            self._pull(t)
            return t, b

    def _merge(self, a, b):
        if a == 0 or b == 0:
            return a or b
        if self.PR[a] > self.PR[b]:
            self._push(a)
            self.R[a] = self._merge(self.R[a], b)
            self._pull(a)
            return a
        else:
            self._push(b)
            self.L[b] = self._merge(a, self.L[b])
            self._pull(b)
            return b

    # public API
    def build_from_list(self, arr):
        if not arr:
            self.root = 0
            return
        idxs = [self._new_node(v) for v in arr]
        st = []
        for idx in idxs:
            last = 0
            while st and self.PR[st[-1]] < self.PR[idx]:
                last = st.pop()
                self._pull(last)
            self.L[idx] = last
            if st:
                self.R[st[-1]] = idx
            st.append(idx)
        while len(st) > 1:
            self._pull(st.pop())
        self.root = st[0] if st else 0
        # finalize
        stack = [self.root]
        while stack:
            u = stack.pop()
            if not u: continue
            self._push(u)
            stack.append(self.R[u]); stack.append(self.L[u])
            self._pull(u)

    def insert(self, pos, x):
        a, b = self._split(self.root, pos)
        mid = self._new_node(x)
        self.root = self._merge(self._merge(a, mid), b)

    def insert_multiple(self, pos, arr):
        if not arr: return
        idxs = [self._new_node(v) for v in arr]
        st = []
        for idx in idxs:
            last = 0
            while st and self.PR[st[-1]] < self.PR[idx]:
                last = st.pop()
                self._pull(last)
            self.L[idx] = last
            if st:
                self.R[st[-1]] = idx
            st.append(idx)
        while len(st) > 1:
            self._pull(st.pop())
        newroot = st[0] if st else 0
        stack = [newroot]
        while stack:
            u = stack.pop()
            if not u: continue
            self._push(u)
            stack.append(self.R[u]); stack.append(self.L[u])
            self._pull(u)
        a, b = self._split(self.root, pos)
        self.root = self._merge(self._merge(a, newroot), b)

    def print_all(self):
        out = []
        st = []
        cur = self.root
        while st or cur:
            while cur:
                self._push(cur)
                st.append(cur)
                cur = self.L[cur]
            cur = st.pop()
            out.append(str(self.VAL[cur]))
            cur = self.R[cur]
        sys.stdout.write(" ".join(out) + "\n")

    def to_list(self):
        out = []
        st = []
        cur = self.root
        while st or cur:
            while cur:
                self._push(cur)
                st.append(cur)
                cur = self.L[cur]
            cur = st.pop()
            out.append(self.VAL[cur])
            cur = self.R[cur]
        return out

    def __iter__(self):
        st = []
        cur = self.root
        while st or cur:
            while cur:
                self._push(cur)
                st.append(cur)
                cur = self.L[cur]
            cur = st.pop()
            yield self.VAL[cur]
            cur = self.R[cur]

    def __getitem__(self, k):
        if k < 0:
            k += self._size(self.root)
        cur = self.root
        while cur:
            self._push(cur)
            lsz = self._size(self.L[cur])
            if k < lsz:
                cur = self.L[cur]
            elif k == lsz:
                return self.VAL[cur]
            else:
                k -= lsz + 1
                cur = self.R[cur]
        raise IndexError("index out of range")

    # range ops
    def range_add(self, l, r, x):
        a, bc = self._split(self.root, l)
        b, c = self._split(bc, r - l)
        if b: self._apply_mul_add(b, 1, x)
        self.root = self._merge(self._merge(a, b), c)

    def range_mul(self, l, r, x):
        a, bc = self._split(self.root, l)
        b, c = self._split(bc, r - l)
        if b: self._apply_mul_add(b, x, 0)
        self.root = self._merge(self._merge(a, b), c)

    def range_update(self, l, r, x):
        a, bc = self._split(self.root, l)
        b, c = self._split(bc, r - l)
        if b: self._apply_set(b, x)
        self.root = self._merge(self._merge(a, b), c)

    def range_reverse(self, l, r):
        a, bc = self._split(self.root, l)
        b, c = self._split(bc, r - l)
        if b: self._apply_rev(b)
        self.root = self._merge(self._merge(a, b), c)

    def range_erase(self, l, r):
        a, bc = self._split(self.root, l)
        b, c = self._split(bc, r - l)
        self.root = self._merge(a, c)

    def range_sum(self, l, r):
        a, bc = self._split(self.root, l)
        b, c = self._split(bc, r - l)
        res = self.SUM[b] if b else 0
        self.root = self._merge(self._merge(a, b), c)
        return res

    def range_max(self, l, r):
        a, bc = self._split(self.root, l)
        b, c = self._split(bc, r - l)
        res = self.MX[b] if b else -10**30
        self.root = self._merge(self._merge(a, b), c)
        return res

    def range_min(self, l, r):
        a, bc = self._split(self.root, l)
        b, c = self._split(bc, r - l)
        res = self.MN[b] if b else 10**30
        self.root = self._merge(self._merge(a, b), c)
        return res
