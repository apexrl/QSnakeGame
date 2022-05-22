import numpy as np

from snake_env.utils import int_to_vec


def vec_to_int(vec):
    res = 0
    for v in vec:
        res = res | 2 ** v
    return res


def test_int_to_vec():
    for _ in range(10):
        vec = np.random.choice(10, 4, replace=False)
        num = vec_to_int(vec)
        assert set(int_to_vec(num)) == set(vec)
