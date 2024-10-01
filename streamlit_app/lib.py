import streamlit as st
import pandas as pd
import plotly
import scipy
import difflib
import bcrypt
import sklearn

print("streamlit:", st.__version__)
print("pandas:", pd.__version__)
print("plotly:", plotly.__version__)
print("scipy:", scipy.__version__)
print("difflib:", difflib.__version__)  # difflib tidak memiliki atribut versi
print("bcrypt:", bcrypt.__version__)
print("sklearn:", sklearn.__version__)
