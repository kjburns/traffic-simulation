import numpy as np 
import cupy as cp
import time 

def do_complex_math(xp):
    start_time = time.process_time()
    x = xp.random.rand(10000) * 100
    y = xp.random.rand(10000) * 100
    x_ij = x[:, xp.newaxis] - x[xp.newaxis, :]
    y_ij = y[:, xp.newaxis] - y[xp.newaxis, :]
    dist_ij = xp.sqrt(x_ij ** 2 + y_ij ** 2)

    end_time = time.process_time()

    print('elapsed time: ', end_time - start_time)

if (__name__ == '__main__'):
    print('using numpy:')
    do_complex_math(np)

    print('using cupy:')
    do_complex_math(cp)
    pass