"""
Tests for PicoBalloons.py. Run with `pytest` from any directory.

Reference values come from two places:

- float1g.xls, the spreadsheet calculator the model was built from. The
  spreadsheet uses a slightly different 97% helium density and a coarser
  atmosphere table lookup, so it is compared with a loose tolerance.
- PicoBalloons.jl, the Julia version of this model. It uses the same tables
  and formulas, so it is compared with a tight tolerance.
"""
import os
import sys

import numpy as np
import pytest
from astropy import units as u

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import PicoBalloons as pb


def system(balloon_g, balloon_m3, payload_g, free_lift_g, gas):
    balloon = pb.Balloon(balloon_g*u.g, balloon_m3*u.m**3)
    return pb.BalloonSystem(balloon, payload_g*u.g, free_lift_g*u.g, gas)


def test_measured_32in_balloon_volume():
    # tape-measure estimate of one 32in balloon, see float1g.qmd
    mass = 36.4 # gram
    c1 = 180 # circumference x2 cm
    c2 = 215 # circumference x1 cm

    a = c1/np.pi/2 # semi-axis radius cm
    b = c1/np.pi/2 # semi-axis radius cm
    c = c2/np.pi/2 # semi-axis radius cm

    volume = 4/3 * np.pi * a * b * c # cm^3
    volume /= 100**3 # m^3

    balloon = pb.Balloon(mass * u.gram, volume * u.meter**3)
    assert balloon.volume.value == pytest.approx(0.118, abs=0.001)
    assert balloon.weight.value == pytest.approx(0.0364)


def test_float1g_spreadsheet_reference():
    # float1g.xls: helium 97%, 6 g free lift, 0.24 m^3, 37 g balloon, 21 g payload
    s = system(37.0, 0.24, 21.0, 6.0, 'helium 97%')
    assert s.neck_lift.to(u.g).value == pytest.approx(27.0)
    assert s.launch_gas_volume.to(u.m**3).value == pytest.approx(0.06251418604, rel=1e-3)
    assert s.total_mass.to(u.kg).value == pytest.approx(0.0705631047, rel=1e-3)
    assert s.system_density.to(u.kg/u.m**3).value == pytest.approx(0.2940129364, rel=1e-3)
    assert s.free_lift_ratio.value == pytest.approx(0.0850302721, rel=1e-3)
    assert s.float_temperature.to(u.deg_C, u.temperature()).value == pytest.approx(-56.46, abs=0.01)
    assert s.internal_pressure.to(u.kPa).value == pytest.approx(19.8462903, rel=1e-3)
    assert s.float_pressure.to(u.kPa).value == pytest.approx(18.2639624, rel=2e-3)
    assert s.super_pressure.to(u.kPa).value == pytest.approx(1.55298969, rel=1e-3)
    # spreadsheet shows altitudes rounded to 10 m
    assert s.float_altitude.to(u.m).value == pytest.approx(12390.0, abs=15.0)
    assert s.super_pressure_onset_altitude.to(u.m).value == pytest.approx(11860.0, abs=15.0)


# (balloon g, balloon m^3, payload g, free lift g, gas) -> values from PicoBalloons.jl
JULIA_CASES = [
    (76.0, 0.236, 16.7, 5.0, 'helium 97%',
     dict(vfill=0.09543811663573314, mass=0.11188306144378236,
          alt=8887.354932814274, dp=1.433864485988979, onset=8507.494631141992)),
    (76.0, 0.236, 16.7, 5.0, 'helium party',
     dict(vfill=0.15899158977708827, mass=0.18971699999999997,
          alt=4196.287138584248, dp=1.6458381268590674, onset=3934.924205507789)),
    (71.0, 0.41, 16.7, 8.0, 'helium 97%',
     dict(vfill=0.09348441926345612, mass=0.10649036827195468,
          alt=13176.034011186513, dp=1.2297817386339485, onset=12704.775460969311)),
    (38.0, 0.118, 0.0, 0.0, 'hydrogen',
     dict(vfill=0.03334795963141729, mass=0.04084124616059675,
          alt=11347.365637068933, dp=0.022013869610545952, onset=11337.422509512566)),
]


@pytest.mark.parametrize('bg,bv,pg,fl,gas,expected', JULIA_CASES)
def test_matches_julia(bg, bv, pg, fl, gas, expected):
    s = system(bg, bv, pg, fl, gas)
    assert s.launch_gas_volume.to(u.m**3).value == pytest.approx(expected['vfill'], rel=1e-9)
    assert s.total_mass.to(u.kg).value == pytest.approx(expected['mass'], rel=1e-9)
    assert s.float_altitude.to(u.m).value == pytest.approx(expected['alt'], rel=1e-9)
    assert s.differential_pressure.to(u.kPa).value == pytest.approx(expected['dp'], rel=1e-6)
    assert s.super_pressure_onset_altitude.to(u.m).value == pytest.approx(expected['onset'], rel=1e-9)


def test_results_are_scalar_with_scalar_inputs():
    s = system(76.0, 0.236, 16.7, 5.0, 'helium 97%')
    assert np.ndim(s.float_altitude.value) == 0
    assert np.ndim(s.launch_gas_volume.value) == 0


def test_vector_free_lift():
    balloon = pb.Balloon(76.0*u.g, 0.236*u.m**3)
    free_lifts = np.arange(0.0, 10.0, 1.0)*u.g
    s = pb.BalloonSystem(balloon, 16.7*u.g, free_lifts, 'helium 97%')
    assert s.float_altitude.shape == (10,)
    # more free lift means more gas and a (slightly) lower float
    assert np.all(np.diff(s.float_altitude.value) < 0)


def test_float_attribute_names_follow_julia():
    s = system(76.0, 0.236, 16.7, 5.0, 'helium 97%')
    for name in ('float_altitude', 'float_temperature', 'float_pressure'):
        assert getattr(s, name) is not None


def test_balloon_too_heavy_to_float_raises():
    # system denser than sea level air, Julia raises here, so must this
    with pytest.raises(ValueError, match='outside the atmosphere table'):
        system(38.0, 0.118, 33.8, 5.0, 'helium party')


def test_unknown_gas_raises():
    with pytest.raises(ValueError, match='unknown gas'):
        system(38.0, 0.118, 10.0, 5.0, 'nitrogen')


def test_overfilled_balloon_raises():
    # 200 g payload needs far more gas than a 0.118 m^3 balloon holds
    with pytest.raises(ValueError):
        system(38.0, 0.118, 200.0, 5.0, 'helium 97%')


def test_works_from_other_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    s = system(76.0, 0.236, 16.7, 5.0, 'helium 97%')
    assert s.float_altitude.to(u.m).value > 0


def test_atmosphere_density_roundtrip():
    atmos = pb.Atmosphere()
    density = atmos.density(6400*u.m)
    assert atmos.altitude(density).to(u.m).value == pytest.approx(6400.0, abs=1e-6)


def test_info_includes_name():
    balloon = pb.Balloon(76.0*u.g, 0.236*u.m**3)
    s = pb.BalloonSystem(balloon, 16.7*u.g, 5.0*u.g, 'helium 97%', name='test')
    assert s.info().startswith('test\n')
