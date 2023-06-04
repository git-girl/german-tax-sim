import numpy as np
import cupy as cp
import time

asize = 10000000
nprand = np.random.rand(asize)
start_time = time.time()
np.cos(nprand)
print("--- %s seconds ---" % (time.time() - start_time))
