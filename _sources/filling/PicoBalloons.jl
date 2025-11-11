module PicoBalloons

export Balloon, BalloonSystem, FloatParameters

using CSV
using DataFrames
using Interpolations
# using Plots
#using Unitful
#using UnitfulUS
using DynamicQuantities
# using Printf
# using PrettyTables

# create an imperial pressure unit psi - pounds per sq inch
# @register_unit psi 6.89476u"kPa"

# there's conversion from Kelvin to degC so create a function for that
# this strips off the units completely and returns the value in degC
kelvin_to_degC_value(k) = ustrip(k .- 0.0ua"degC")
degC_value_to_kelvin(c) = (c .+ ustrip(0.0ua"degC"))u"K"

# environmental parameter

atmosphere_pressure_msl = 101.325u"kPa" # kPa at MSL "standard pressure"
atmosphere_temperature_msl = 15.0ua"degC"
# atmosphere_temperature_msl_c = 15.0
# atmosphere_temperature_msl = 273.1 + atmosphere_temperature_msl_c # Kelvin at standard temperature

## Define atmospheric profile
#fpath = "/opt/project/_sources/filling"
# in this table, the P/T column is just the ration of the Pressure/(Temperature converted to Kelvin)
df_atmos = CSV.read(joinpath(@__DIR__,"atmos.csv"), DataFrame)



"Return the atmospheric pressure as a quantity at the given density"
function atmos_pressure(density; df_atmos=df_atmos)
    u_density = ustrip(density/u"kg/m^3")
    LinearInterpolation(
            df_atmos.var"Den (Kg/cu m)",
            df_atmos.var"Pres (kPa)")(u_density)u"kPa"
end

"Return the atmospheric temperature as a function of system desnity"
function atmos_temperature(density; df_atmos=df_atmos)
    u_density = ustrip(density/u"kg/m^3")
    degC = LinearInterpolation(
            df_atmos.var"Den (Kg/cu m)",
        df_atmos.var"Temp (C)")(u_density)
    degC_value_to_kelvin(degC)
end

"Return the altitude of a given density"
function atmos_altitude(density; df_atmos=df_atmos)
    u_density = ustrip(density/u"kg/m^3")
    LinearInterpolation(
            df_atmos.var"Den (Kg/cu m)",
            df_atmos.var"Alt (m)")(u_density)u"m" # meters
end

"Return the density of a given altitude"
function atmos_density(altitude; df_atmos=df_atmos)
    u_altitude = ustrip(altitude/u"m")
    LinearInterpolation(
            reverse(df_atmos.var"Alt (m)"),
            reverse(df_atmos.var"Den (Kg/cu m)"))(u_altitude)u"kg/m^3"
end

"DataFrame holding the gas densities"
df_gas = CSV.read("""
        "name","0deg","15deg"
        "hydrogen",0.0899,0.0852
        "helium",0.1786,0.1693
        "helium 97%",0.2120,0.2010
        "helium party",0.6102020876451465,0.6102020876451465
        "air",1.2920,1.2247
    """ |> IOBuffer, DataFrame)

"Return the density of the chosen gas"
function gas_density(
    gas,
    df_gas = df_gas,
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
    launch_gas_volume
    lift_gas_mass
    total_mass
    system_density
    free_lift_ratio

    # these are computed float parameters
    float_temperature
    float_altitude
    float_pressure
    internal_pressure
    differential_pressure
    super_pressure
    super_pressure_onset_altitude

    function BalloonSystem(balloon,payload_weight,free_lift,gas)
        neck_lift = free_lift .+ payload_weight
        lift_gas_density = gas_density(gas)
        air_density = gas_density("air")
        launch_gas_volume = (neck_lift .+ balloon.weight)./(air_density .- lift_gas_density)
        lift_gas_mass = lift_gas_density .* launch_gas_volume
        total_mass = lift_gas_mass .+ payload_weight .+ balloon.weight
        system_density = total_mass ./ balloon.volume
        free_lift_ratio = free_lift ./ (balloon.weight .+ payload_weight .+ lift_gas_mass)

        temperature_at_float = atmos_temperature(system_density)
        pressure_at_float = atmos_pressure(system_density)
        balloon_altitude = atmos_altitude(system_density)

        internal_pressure =
            (atmosphere_pressure_msl .* launch_gas_volume) ./ atmosphere_temperature_msl .* ( temperature_at_float) ./ balloon.volume

        differential_pressure = internal_pressure .- pressure_at_float

        kov = launch_gas_volume./balloon.volume .* df_atmos.var"P/T (kPa/K)"[end]u"kPa/K"
        super_pressure_onset_altitude =
            LinearInterpolation(df_atmos.var"P/T (kPa/K)",
                                df_atmos.var"Alt (m)")( (kov |> us"kPa/K").value  )u"m" # meter
        super_pressure = pressure_at_float .* free_lift_ratio
        
        new(
            balloon,
            payload_weight,
            free_lift,
            gas,
            lift_gas_density,
            air_density,
            neck_lift,
            launch_gas_volume,
            lift_gas_mass,
            total_mass,
            system_density,
            free_lift_ratio,
            temperature_at_float,
            balloon_altitude,
            pressure_at_float,
            internal_pressure,
            differential_pressure,
            super_pressure,
            super_pressure_onset_altitude
        )
    end
end

function Base.println(bs::BalloonSystem)

    println(bs.balloon)
    println("Neck lift                         $(bs.neck_lift |> us"g")")
    println("Gas fill at launch                $(bs.launch_gas_volume)")
    println("Gas mass                          $(bs.lift_gas_mass |> us"g")")
    println("Total mass                        $(bs.total_mass |> us"g")")
    println("System density                    $(bs.system_density)")
    println("Temperature at float              $(bs.float_temperature)")
    println("Pressure at float                 $(bs.float_pressure |> us"kPa")")
    println("Float altitude                    $(bs.float_altitude)")
    println("Internal pressure                 $(bs.internal_pressure |> us"kPa")")
    println("Differential pressure             $(bs.differential_pressure |> us"kPa")")
    println("Super pressure                    $(bs.super_pressure |> us"kPa")")
    println("Super pressure onset altitude     $(bs.super_pressure_onset_altitude)")

end




## Define gas properties
# Gas density table in kg/cu m at 101.325 kPa at MSL



## Computed balloon fill properties 

# chosen_gas_density = only(df_gas[(df_gas.name .== gas),"15deg"])u"kg/m^3"
# air_density = only(df_gas[(df_gas.name .== "air"),"15deg"])u"kg/m^3"
# neck_lift = bs.free_lift + bs.payload_weight # gram
# launch_gas_fill =
#     (neck_lift + bs.balloon.weight)/
#     (air_density-chosen_gas_density)#/1000.0

# # system denisty is the total mass including payload
# # divided by the balloon volume
# gas_mass = chosen_gas_density * launch_gas_fill# * 1000 # gram
# total_mass = gas_mass + bs.payload_weight + bs.balloon.weight # gram
# #total_mass /= 1000 # convert to kg
# system_density = total_mass / bs.balloon.volume # kg/m^3

# println("Neck lift          $(neck_lift |> us"g")")
# println("Gas fill at launch $(launch_gas_fill)")
# println("Gas mass           $(gas_mass |> us"g")")
# println("Total mass         $(total_mass |> us"g")")
# println("System density     $(system_density)")





end # module
