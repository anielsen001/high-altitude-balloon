include("float1g.jl")

using DynamicQuantities
using .PicoBalloons

free_lift = 5.0u"g" # grams
balloon_weight = 38.0u"g" # gram
balloon_volume = 0.15u"m^3" # m^3
payload_weight = 20.0u"g" # gram
gas = "helium 97%"

balloon = Balloon(balloon_weight, balloon_volume)
bs = BalloonSystem(balloon, payload_weight, free_lift, gas)
println(bs)


payload_weights = [15.0,20.0,25.0]u"g"
bss = BalloonSystem(balloon, payload_weights, free_lift, gas)
