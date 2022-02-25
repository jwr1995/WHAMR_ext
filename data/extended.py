import numpy as np
import pandas as pd

np.random.seed(1234)

for set in ['tt','tr','cv']:
 df = pd.read_csv("reverb_params_"+set+".csv")
 t60s = np.random.rand(len(df))*2+1
 print(len(t60s),max(t60s),min(t60s))
 df["T60"] = t60s
 print(df)
 df.to_csv("ext_reverb_params_"+set+".csv",index=False)
