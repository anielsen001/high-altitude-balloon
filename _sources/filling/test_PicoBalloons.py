import numpy as np

mass = 36.4 # gram
c1 = 180 # circumference x2 cm
c2 = 215 # circumference x1 cm

a = c1/np.pi/2 # semi-axis radius cm
b = c1/np.pi/2 # semi-axis radius cm
c = c2/np.pi/2 # semi-axis radius cm

volume = 4/3 * np.pi * a * b * c # cm^3
volume /= 100^3 # m^3

balloon = Balloon(mass * u.gram, volume * u.meter**3)
