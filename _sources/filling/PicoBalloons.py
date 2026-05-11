from astropy import units as u
from io import StringIO
from matplotlib import pylab as plt
import numpy as np
import pandas as pd

atmosphere_pressure_msl = 101.325*u.kPa # kPa at MSL "standard pressure"
atmosphere_temperature_msl = 15.0ua"degC"

## Define atmospheric profile
#fpath = "/opt/project/_sources/filling"
# in this table, the P/T column is just the ration of the Pressure/(Temperature converted to Kelvin)
df_atmos = pd.read_csv("atmos.csv")

# this table contains the density of different gasses at 0 deg and 15 deg Celsius
gas_csv = """
"name","0deg","15deg"
"hydrogen",0.0899,0.0852
"helium",0.1786,0.1693
"helium 97%",0.2120,0.2010
"helium party",0.6102020876451465,0.6102020876451465
"air",1.2920,1.2247
"""

# create a pandas dataframe from the gas density csv
df_gas = pd.read_csv(StringIO(gas_csv))

def gas_density(
        gas_name,
        df_gas = df_gas,
        gas_temp = 15,
        ):
    """
    return the named gas density with units attached
    """
    if gas_temp == 15:
        tempstr = '15deg'
    elif gas_temp == 0:
        tempstr = '0deg'
    else:
        raise ValueError("gas_temp must be 0 or 15")

    density = df_gas[df_gas['name']==gas_name][tempstr].to_numpy()*u.kg/u.m**3

    return density
