from astropy import units as u
from io import StringIO
from matplotlib import pylab as plt
import numpy as np
import pandas as pd
import scipy.interpolate as spi

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

## Define atmospheric profile
#fpath = "/opt/project/_sources/filling"
# in this table, the P/T column is just the ration of the Pressure/(Temperature converted to Kelvin)
df_atmos = pd.read_csv("atmos.csv")

class Atmosphere():

    # atmospheric profile data frame
    df_atmos = None

    # interplators
    interp_pressure = None
    interp_temperature = None
    interp_altitude = None
    interp_density = None

    def __init__(
            self,
            atmosfile = 'atmos.csv',
            ):

        # read the atmospheric profile to a data frame
        self.df_atmos = pd.read_csv("atmos.csv")

        # create interpolators
        # these are created here so they are only created once
        # and then called when needed
        self.interp_pressure = spi.make_interp_spline(
            self.df_atmos['Den (Kg/cu m)'].to_numpy(),
            self.df_atmos['Pres (kPa)'].to_numpy(),
            k=1,
            )

        self.interp_temperature = spi.make_interp_spline(
            self.df_atmos['Den (Kg/cu m)'].to_numpy(),
            self.df_atmos['Temp (C)'].to_numpy(),
            k=1,
            )

        self.interp_altitude = spi.make_interp_spline(
            self.df_atmos['Den (Kg/cu m)'].to_numpy(),
            self.df_atmos['Alt (m)'].to_numpy(),
            k=1,
            )

        self.interp_density = spi.make_interp_spline(
            self.df_atmos['Alt (m)'].to_numpy(),
            self.df_atmos['Den (Kg/cu m)'].to_numpy(),
            k=1,
            )
        

    def pressure(
            self,
            density,
            ):
        """
        Return the atmospheric pressure at a given density

        Parameters
        ----------
        density :
          quantity of km/m**3, i.e. 10*u.kg/u.m**3

        Returns
        -------
        pressure
          quantity of kPa
        """

        # get just the value from the density quantity
        u_density = density.value

        # get return value
        pressure = self.interp_pressure(u_density) * u.kPa

        return pressure

    def temperature(
            self,
            density,
            ):
        """
        Return the atmospheric temperature at a given density

        Parameters
        ----------
        density :
          quantity of km/m**3, i.e. 10*u.kg/u.m**3

        Returns
        -------
        temperature
          quantity of Kelvin
        """

        # get just the value from the density quantity
        u_density = density.value

        # get return value - will be in Centigrade
        tempC = self.interp_temperature(u_density) * u.Celsius
        tempK = tempC.to(u.K, equivalencies=u.temperature())

        return tempK       
        
        

class Balloon():
    weight = None
    volume = None
    name = None

    def __init__(
            self,
            weight,
            volume,
            name=None,
    ):
        self.weight = weight
        self.volume = volume
        self.name= name

    def namestr(self):
        if self.name is None:
            return f'Weight: {self.weight}, Volume: {self.volume}'
        return f'{self.name}: Weight: {self.weight}, Volume: {self.volume}'

    def __str__(self):
        return self.namestr()

    def __repr__(self):
        return self.namestr()

    def __add__(self,other):
        return Balloon(self.weight + other.weight, self.volume + other.volume)

    def __mul__(self,other):
        return Balloon(self.weight * other, self.volume * other)

    def __rmul__(self,other):
        return Balloon(self.weight * other, self.volume * other)

class BalloonSystem():

    # optional
    name = None
    
    # these are required
    balloon = None
    payload_weight = None
    free_lift = None
    gas = None

    # these could be computed
    gas_density = None
    air_density = None
    neck_lift = None
    launch_gas_volume = None
    lift_gas_mass = None
    total_mass = None
    system_density = None
    free_lift_ratio = None

    # these are computed float parameters
    float_temperature = None
    float_altitude = None
    float_pressure = None
    internal_pressure = None
    differential_pressure = None
    super_pressure = None
    super_pressure_onset_altitude = None  

    def __init__(
            self,
            balloon,
            payload_weight,
            free_lift,
            gas,
            name = None,
            ):

        # copy input parameters
        self.balloon = balloon
        self.payload_weight = payload_weight
        self.free_lift = free_lift
        self.gas = gas
        self.name = name
        
        neck_lift = free_lift + payload_weight
        lift_gas_density = gas_density(gas)
        air_density = gas_density("air")
        launch_gas_volume = (neck_lift + balloon.weight)/(air_density - lift_gas_density)
        lift_gas_mass = lift_gas_density * launch_gas_volume
        total_mass = lift_gas_mass + payload_weight + balloon.weight
        system_density = total_mass / balloon.volume
        free_lift_ratio = free_lift / (balloon.weight + payload_weight + lift_gas_mass)

        temperature_at_float = atmos_temperature(system_density)
        pressure_at_float = atmos_pressure(system_density)
        balloon_altitude = atmos_altitude(system_density)

        internal_pressure =
            (atmosphere_pressure_msl * launch_gas_volume) / atmosphere_temperature_msl * ( temperature_at_float) / balloon.volume

        differential_pressure = internal_pressure - pressure_at_float

        kov = launch_gas_volume/balloon.volume * df_atmos.var"P/T (kPa/K)"[end]u"kPa/K"
        super_pressure_onset_altitude =
            LinearInterpolation(df_atmos.var"P/T (kPa/K)",
                                df_atmos.var"Alt (m)")( (kov |> us"kPa/K").value  )u"m" # meter
        super_pressure = pressure_at_float * free_lift_ratio
