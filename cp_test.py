import numpy as np
import cupy as cp
import time

asize = 10000000
nprand = np.random.rand(asize)
cprand = cp.array(nprand)

start_time = time.time()
cp.cos(cprand)
print("--- %s seconds ---" % (time.time() - start_time))
