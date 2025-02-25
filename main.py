from pathlib import Path
import pandas as pd
import numpy as np

df = pd.read_csv('data\MdotfromMRATE_A', delim_whitespace=True)
print(df)
