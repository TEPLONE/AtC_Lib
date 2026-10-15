import bisect
def LIS(seq):
    """return len(LIS) by O(NlogN)"""
    ans = 0
    if seq:
        LIS = [seq[0]]
        for i in range(len(seq)):
            if seq[i] > LIS[-1]:
                LIS.append(seq[i])
            else:
                LIS[bisect.bisect_left(LIS, seq[i])] = seq[i]
        ans += len(LIS)
    return ans
