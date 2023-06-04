import numpy as np
import cupy as cp

type_dict = {
    'double': np.float64,
    'BigDecimal': np.float64,
    'BigDecimal[]': cp.ndarray,
    'int': np.int64
}
