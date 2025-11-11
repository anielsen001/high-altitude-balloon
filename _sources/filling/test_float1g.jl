include("PicoBalloons.jl")

using Plots
using Revise
using DynamicQuantities
using .PicoBalloons

free_lift = 5.0u"g" # grams
balloon_weight = 38.0u"g" # gram
balloon_volume = 0.15u"m^3" # m^3
payload_weight = 16.7u"g" # gram
gas = "helium 97%"

balloon = Balloon(balloon_weight, balloon_volume)
balloon_2 = balloon * 2
bs = BalloonSystem(balloon, payload_weight, free_lift, gas)
bs2 = BalloonSystem(balloon_2, payload_weight, free_lift, gas)
println(bs)


payload_weights = [15.0,20.0,25.0]u"g"
bss = BalloonSystem(balloon, payload_weights, free_lift, gas)
bss2 = BalloonSystem(balloon_2, payload_weights, free_lift, gas)

payload_weights = collect(0.0:1.0:50.0)u"g"
bss = BalloonSystem(balloon, payload_weights, free_lift, gas)
bss2 = BalloonSystem(balloon_2, payload_weights, free_lift, gas)


plot(
    ustrip(u"g",payload_weights),
    ustrip(us"ft",bss.float_altitude)/1000.,
    title="Altitude vs. payload weight",
    xlabel="Payload mass [grams]",
    ylabel="Float altitude [kft]",
)
plot!(ustrip(u"g",payload_weights),
    ustrip(us"ft",bss2.float_altitude)/1000.,
    title="Altitude vs. payload weight",
    xlabel="Payload mass [grams]",
    ylabel="Float altitude [kft]",
)
gui()


## invert float altitude to get lift gas density
float_altitude = 6400.0u"m"
system_density = PicoBalloons.atmos_density(6400u"m")
total_mass = system_density * balloon_2.volume
lift_gas_mass = total_mass - payload_weight - balloon_2.weight
lift_gas_density = lift_gas_mass * PicoBalloons.gas_density("air")/(bs2.neck_lift + balloon_2.weight + lift_gas_mass)
# = 0.6102020876451465 m⁻³ kg


## work this answer forward again to verify the float altitude
gas = "helium party"

balloon = Balloon(balloon_weight, balloon_volume)
balloon_2 = balloon * 2
bs = BalloonSystem(balloon, payload_weight, free_lift, gas)
bs2 = BalloonSystem(balloon_2, payload_weight, free_lift, gas)
println(bs)

# Weight: 0.038 kg
# Volume: 0.15 m³
# Neck lift                         21.7 g
# Gas fill at launch                0.09715248628139377 m³
# Gas mass                          59.28264994882293 g
# Total mass                        113.98264994882292 g
# System density                    0.7598843329921529 m⁻³ kg
# Temperature at float              257.528258794135 K
# Pressure at float                 56.13300078221867 kPa
# Float altitude                    4724.459353754233 m
# Internal pressure                 58.65236658085537 kPa
# Differential pressure             2.519365798636696 kPa
# Super pressure                    2.462348471781531 kPa
# Super pressure onset altitude     4307.524755728726 m
