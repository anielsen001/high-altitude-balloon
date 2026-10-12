"""
Pico balloon float calculations.

Python port of PicoBalloons.jl, validated against float1g.xls (Steve Randall's
superpressure balloon float calculator, version 1g) and against the Julia
module. See test_PicoBalloons.py.

The model treats the balloon as a sealed, fixed-volume envelope. It floats at
the altitude where the density of the surrounding air equals the total system
mass (balloon + payload + lift gas) divided by the balloon volume.
"""
from functools import lru_cache
from io import StringIO
from pathlib import Path

from astropy import units as u
import numpy as np
import pandas as pd

atmosphere_pressure_msl = 101.325*u.kPa # kPa at MSL "standard pressure"
atmosphere_temperature_msl = (15.0*u.Celsius).to(u.K, equivalencies=u.temperature())

# atmos.csv lives next to this file, so this works from any working directory
DEFAULT_ATMOS_FILE = Path(__file__).resolve().parent / "atmos.csv"

@lru_cache(maxsize=None)
def _read_atmos(atmosfile):
    """
    Read the atmospheric profile table once per file.

    In this table, the P/T column is just the ratio of the pressure to the
    temperature converted to Kelvin. Rows run from high altitude (low density)
    to sea level (high density).
    """
    return pd.read_csv(atmosfile)

df_atmos = _read_atmos(DEFAULT_ATMOS_FILE)

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

    match = df_gas[df_gas['name']==gas_name][tempstr]
    if len(match) != 1:
        raise ValueError(
            f"unknown gas {gas_name!r}, choose from {list(df_gas['name'])}"
        )

    return match.iloc[0]*u.kg/u.m**3

class Atmosphere():
    """
    Atmospheric profile with linear interpolation of the table in atmos.csv.

    Like the Julia version, an input outside the table raises ValueError
    instead of silently extrapolating.
    """

    def __init__(
            self,
            atmosfile = None,
            ):

        if atmosfile is None:
            atmosfile = DEFAULT_ATMOS_FILE

        # read the atmospheric profile to a data frame
        self.df_atmos = _read_atmos(Path(atmosfile))

        self._density = self.df_atmos['Den (Kg/cu m)'].to_numpy()
        self._pressure = self.df_atmos['Pres (kPa)'].to_numpy()
        self._temperature = self.df_atmos['Temp (C)'].to_numpy()
        self._altitude = self.df_atmos['Alt (m)'].to_numpy()
        self._p_over_t = self.df_atmos['P/T (kPa/K)'].to_numpy()

    @staticmethod
    def _interp(x, xp, fp, what):
        """linear interpolation which refuses to extrapolate"""
        x = np.asarray(x, dtype=float)
        if np.any(x < xp.min()) or np.any(x > xp.max()):
            raise ValueError(
                f"{what} outside the atmosphere table "
                f"[{xp.min():g}, {xp.max():g}]: {x}"
            )
        return np.interp(x, xp, fp)

    def _by_density(self, density, column):
        value = density.to(u.kg/u.m**3).value
        return self._interp(
            value, self._density, column, "system density (kg/m^3)",
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
          quantity of kg/m**3, i.e. 10*u.kg/u.m**3

        Returns
        -------
        pressure
          quantity of kPa
        """
        return self._by_density(density, self._pressure) * u.kPa

    def temperature(
            self,
            density,
            ):
        """
        Return the atmospheric temperature at a given density

        Parameters
        ----------
        density :
          quantity of kg/m**3, i.e. 10*u.kg/u.m**3

        Returns
        -------
        temperature
          quantity of Kelvin
        """
        tempC = self._by_density(density, self._temperature) * u.Celsius
        return tempC.to(u.K, equivalencies=u.temperature())

    def altitude(
            self,
            density,
            ):
        """
        Return the altitude at which the air has a given density

        Parameters
        ----------
        density :
          quantity of kg/m**3, i.e. 10*u.kg/u.m**3

        Returns
        -------
        altitude
          meters
        """
        return self._by_density(density, self._altitude) * u.meter

    def density(
            self,
            altitude,
            ):
        """
        Return the air density at a given altitude

        Parameters
        ----------
        altitude :
          quantity of length, i.e. 6400*u.m

        Returns
        -------
        density
          quantity of kg/m**3
        """
        value = altitude.to(u.m).value
        # the table runs from high altitude to sea level, np.interp needs
        # increasing x, so flip it
        return self._interp(
            value, self._altitude[::-1], self._density[::-1], "altitude (m)",
        ) * u.kg/u.m**3

    def onset_altitude(
            self,
            p_over_t,
            ):
        """
        Return the altitude at which the atmosphere has a given P/T ratio

        Parameters
        ----------
        p_over_t :
          quantity of kPa/K
        """
        value = p_over_t.to(u.kPa/u.K).value
        return self._interp(
            value, self._p_over_t, self._altitude, "P/T (kPa/K)",
        ) * u.meter

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
        """
        create a Balloon object.

        Parameters
        ----------
        weight
        weight/mass of balloon with units attached. i.e. 30 * u.gram
        volume
        volume of balloon with units attached i.e. 100 * u.meter**3
        """

        # .decompose converts into base kms units, even if grams are used as input
        self.weight = weight.decompose()
        self.volume = volume.decompose()
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
    """
    A balloon, its payload, and the lift gas, with the computed float state.

    Attribute names follow PicoBalloons.jl (float_altitude, float_temperature,
    float_pressure, ...).
    """

    def __init__(
            self,
            balloon,
            payload_weight,
            free_lift,
            gas,
            name = None,
            atmosfile = None,
            ):

        # copy input parameters
        self.balloon = balloon
        self.payload_weight = payload_weight.decompose()
        self.free_lift = free_lift.decompose()
        self.gas = gas
        self.name = name

        self.atmos = Atmosphere(atmosfile)

        neck_lift = self.free_lift + self.payload_weight
        lift_gas_density = gas_density(gas)
        air_density = gas_density("air")
        launch_gas_volume = (neck_lift + balloon.weight)/(air_density - lift_gas_density)
        lift_gas_mass = lift_gas_density * launch_gas_volume
        total_mass = lift_gas_mass + self.payload_weight + balloon.weight
        system_density = total_mass / balloon.volume
        free_lift_ratio = (
            self.free_lift / (balloon.weight + self.payload_weight + lift_gas_mass)
        ).decompose()

        float_temperature = self.atmos.temperature(system_density)
        float_pressure = self.atmos.pressure(system_density)
        float_altitude = self.atmos.altitude(system_density)

        internal_pressure = (
            (atmosphere_pressure_msl * launch_gas_volume)
            / atmosphere_temperature_msl
            * float_temperature
            / balloon.volume
        ).to(u.kPa)

        differential_pressure = internal_pressure - float_pressure

        # the envelope becomes full (superpressure starts) when the ambient
        # P/T falls to the launch P/T scaled by launch volume / balloon volume
        kov = (
            launch_gas_volume / balloon.volume
            * self.atmos.df_atmos['P/T (kPa/K)'].to_numpy()[-1] * u.kPa/u.Kelvin
        )
        super_pressure_onset_altitude = self.atmos.onset_altitude(kov)

        super_pressure = (float_pressure * free_lift_ratio).to(u.kPa)

        self.gas_density = lift_gas_density
        self.air_density = air_density
        self.neck_lift = neck_lift
        self.launch_gas_volume = launch_gas_volume
        self.lift_gas_mass = lift_gas_mass
        self.total_mass = total_mass
        self.system_density = system_density
        self.free_lift_ratio = free_lift_ratio
        self.float_temperature = float_temperature
        self.float_altitude = float_altitude
        self.float_pressure = float_pressure
        self.internal_pressure = internal_pressure
        self.differential_pressure = differential_pressure
        self.kov = kov
        self.super_pressure = super_pressure
        self.super_pressure_onset_altitude = super_pressure_onset_altitude

    def msgstr(self):
        msg = [
            f'{_k}:\t{_v}' for _k,_v in vars(self).items()
            if _k != 'atmos'
        ]

        return '\n'.join(msg)

    def __str__(self):
        return self.msgstr()

    def __repr__(self):
        return self.msgstr()

    def info(self):
        msg = ''
        if self.name is not None:
            msg = f'{self.name}\n'

        msg += \
            f'Altitude:\t{self.float_altitude}\t{self.float_altitude.to(u.imperial.foot)}\n'

        return msg
