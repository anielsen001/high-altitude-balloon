



## Set up

### Package environment

```{julia}
#| label: configure-packages
using Pkg

Pkg.activate(".")

needed_pkgs = [
    "CSV",
    "DataFrames",
    "Interpolations",
    "Plots",
    "DynamicQuantities",
    "Markdown",
    "PrettyTables",
    "Revise",
    "Tables",
    "MarkdownTables"
]
Pkg.add(needed_pkgs)
```

### Imports

```{julia}
#| lable: load-packages
using CSV
using DataFrames
using Interpolations
using Plots
#using Unitful
#using UnitfulUS
using DynamicQuantities
using Printf
using PrettyTables

# create an imperial pressure unit psi - pounds per sq inch
# @register_unit psi 6.89476u"kPa"

# there's conversion from Kelvin to degC so create a function for that
# this strips off the units completely and returns the value in degC
kelvin_to_degC_value(k) = ustrip(k - 0.0ua"degC")
```

## Balloon system properties

```{julia}
#| label: definitions

# environmental parameter

atmosphere_pressure_msl = 101.325u"kPa" # kPa at MSL "standard pressure"
atmosphere_temperature_msl = 15.0ua"degC"
# atmosphere_temperature_msl_c = 15.0
# atmosphere_temperature_msl = 273.1 + atmosphere_temperature_msl_c # Kelvin at standard temperature

function gas_density(
    gas,
    df_gas = CSV.read("""
        "name","0deg","15deg"
        "hydrogen",0.0899,0.0852
        "helium",0.1786,0.1693
        "helium 97%",0.2120,0.2010
        "air",1.2920,1.2247
    """ |> IOBuffer, DataFrame)
)
    density = only(df_gas[(df_gas.name .== gas),"15deg"])u"kg/m^3"

end




"Physical characteristics of a balloon"
struct Balloon
    weight
    volume
end

function Base.print(balloon::Balloon)
    print("Weight: $(balloon.weight), Volume: $(balloon.volume)")
end

function Base.println(balloon::Balloon)
    println("Weight: $(balloon.weight)")
    println("Volume: $(balloon.volume)")
end

Base.:*(balloon::Balloon, n::Real) = Balloon(balloon.weight*n, balloon.volume*n)
Base.:*(n::Real, balloon::Balloon) = Balloon(balloon.weight*n, balloon.volume*n)



"Parameters of a super-pressure balloon system"
mutable struct BalloonSystem
    balloon::Balloon
    payload_weight
    free_lift
    gas::String

    # these could be computed
    gas_density
    air_density
    neck_lift
    launch_gas_fill
    gas_mass
    total_mass
    system_density

    function BalloonSystem(ballon,payload_weight,free_lift,gas)
        neck_lift = free_lift + payload_weight
        
    end
end

"Parameters of a super-pressure balloon at float"
struct FloatParameters
    temperature
    altitude
    free_lift_ratio
    internal_pressure
    external_pressure
    differential_pressure
    super_pressure
    super_pressure_onset_altitude
end

free_lift = 5.0u"g" # grams
balloon_weight = 38.0u"g" # gram
balloon_volume = 0.15u"m^3" # m^3
payload_weight = 20.0u"g" # gram
gas = "helium 97%"

balloon = Balloon(balloon_weight, balloon_volume)
bs = BalloonSystem(balloon, payload_weight, free_lift, gas)

```

## Define gas properties

Gas density table in kg/cu m at 101.325 kPa at MSL

```{julia}
#| label: define-gas-properties
df_gas = CSV.read("""
    "name","0deg","15deg"
    "hydrogen",0.0899,0.0852
    "helium",0.1786,0.1693
    "helium 97%",0.2120,0.2010
    "air",1.2920,1.2247
""" |> IOBuffer, DataFrame)

atmosphere_pressure_msl = 101.325u"kPa" # kPa at MSL "standard pressure
atmosphere_temperature_msl = 15.0ua"degC"
# atmosphere_temperature_msl_c = 15.0
# atmosphere_temperature_msl = 273.1 + atmosphere_temperature_msl_c # Kelvin at standard temperature
df_gas
```

## Computed balloon fill properties 

```{julia}
chosen_gas_density = only(df_gas[(df_gas.name .== gas),"15deg"])u"kg/m^3"
air_density = only(df_gas[(df_gas.name .== "air"),"15deg"])u"kg/m^3"
neck_lift = bs.free_lift + bs.payload_weight # gram
launch_gas_fill =
    (neck_lift + bs.balloon.weight)/
    (air_density-chosen_gas_density)#/1000.0

# system denisty is the total mass including payload
# divided by the balloon volume
gas_mass = chosen_gas_density * launch_gas_fill# * 1000 # gram
total_mass = gas_mass + bs.payload_weight + bs.balloon.weight # gram
#total_mass /= 1000 # convert to kg
system_density = total_mass / bs.balloon.volume # kg/m^3

println("Neck lift          $(neck_lift |> us"g")")
println("Gas fill at launch $(launch_gas_fill)")
println("Gas mass           $(gas_mass |> us"g")")
println("Total mass         $(total_mass |> us"g")")
println("System density     $(system_density)")
```


## Define atmospheric profile

```{julia}
#| label: load-atmospheric-data
fpath = "/opt/project/_sources/filling"
fname = "atmos.csv"
df_atmos = CSV.read(joinpath(fpath,fname), DataFrame);
df_atmos
```

```{julia}
#| label: fig-atmospheric-data-pressure
#| fig-cap: Atmospheric pressure as a function of altitude
plot(
    df_atmos.var"Alt (m)",
    df_atmos.var"Pres (kPa)",
    legend=false,
    xlabel="Altitude [meters]",
    ylabel="Pressure [kPa]",
)
```

```{julia}
#| label: fig-atmospheric-data-temperature
#| fig-cap: Atmospheric temperature as a function of altitude
plot(
    df_atmos.var"Alt (m)",
    df_atmos.var"Temp (C)",
    legend=false,
    xlabel="Altitude [meters]",
    ylabel="Temperature [C]",
)
```



## Float calculations

```{julia}
#| label: float-calculations
# interpolate temperature based on density
u_system_density = ustrip(u"kg/m^3",system_density)
temperature_at_float = LinearInterpolation(df_atmos.var"Den (Kg/cu m)",df_atmos.var"Temp (C)")(u_system_density)ua"degC"
internal_pressure =  (atmosphere_pressure_msl * launch_gas_fill ) / atmosphere_temperature_msl * ( temperature_at_float) / bs.balloon.volume
external_pressure = LinearInterpolation(df_atmos.var"Den (Kg/cu m)",df_atmos.var"Pres (kPa)")(u_system_density)u"kPa"
balloon_altitude = LinearInterpolation(df_atmos.var"Den (Kg/cu m)",df_atmos.var"Alt (m)")(u_system_density)u"m" # meters
# balloon_altitude_feet = balloon_altitude_meter * 3.28

free_lift_ratio = free_lift / (balloon_weight + payload_weight + gas_mass)

differential_pressure = internal_pressure - external_pressure # kPa

k = launch_gas_fill * df_atmos.var"P/T (kPa/K)"[end]u"kPa/K"
kov = k / balloon_volume
(kov |> us"kPa/K").value
superpressure_onset_altitude = LinearInterpolation(df_atmos.var"P/T (kPa/K)", df_atmos.var"Alt (m)")( (kov |> us"kPa/K").value  )u"m" # meter
superpressure = external_pressure * free_lift_ratio

println("Float temperature:       $(temperature_at_float)")
println("Balloon altitude:        $(balloon_altitude)")
println("Balloon altitude:        $(balloon_altitude |> us"ft")")
println("Free lift ratio:         $(free_lift_ratio)")
println("Internal pressure:       $(internal_pressure |> us"kPa")")
println("External pressure:       $(external_pressure |> us"kPa")")
println("Differential pressure:   $(differential_pressure |> us"kPa" )")
println("Super pressure:          $(superpressure |> us"kPa" )")
println("Super pressure altitute: $(superpressure_onset_altitude)")
println("                       : $(superpressure_onset_altitude |> us"ft")")

```

## Float dependencies

How does the float altitude depend upon mass of payload for a fixed balloon.

