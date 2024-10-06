# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 12:01:47 2019

@author: esol
"""
from neqsim.process import (
    clearProcess,
    compressor,
    heater,
    mixer,
    recycle,
    runProcess,
    separator,
    stream,
    valve,
    viewProcess,
)
from neqsim.thermo import fluid, phaseenvelope

feedPressure = 30.0
MPpressure = 10.0
LPpressure = 2.1

# Start by creating a fluid in neqsim
fluid1 = fluid("srk")  # create a fluid using the SRK-EoS
fluid1.addComponent("nitrogen", 1.0)
fluid1.addComponent("CO2", 2.0)
fluid1.addComponent("methane", 85.0)
fluid1.addComponent("ethane", 5.0)
fluid1.addComponent("propane", 3.0)
fluid1.addComponent("i-butane", 2.0)
fluid1.addComponent("n-butane", 2.0)
fluid1.addComponent("n-hexane", 1.1)
fluid1.addComponent("n-heptane", 2.1)
fluid1.addComponent("n-octane", 1.1)
fluid1.addComponent("n-nonane", 0.51)
fluid1.addComponent("nC10", 5.1)
fluid1.setMixingRule("classic")
fluid1.setTemperature(35.15, "C")
fluid1.setPressure(feedPressure, "bara")
fluid1.setTotalFlowRate(10.0, "MSm3/day")


# demonstration of setting up a simple process calculation
clearProcess()
stream1 = stream('stream1', fluid1)
separator1 = separator("inlet separator", stream1)
valve1 = valve("HP oil valve", separator1.getLiquidOutStream(), MPpressure)
separator2 = separator('sep3', valve1.getOutStream())
valve2 = valve('valv4', separator2.getLiquidOutStream(), LPpressure)
separator3 = separator('se55', valve2.getOutStream())

compressorLP1 = compressor('comp1', separator3.getGasOutStream(), MPpressure)
coolerMP1 = heater('heat1', compressorLP1.getOutStream())
coolerMP1.setOutTemperature(303.0)
scrubberLP = separator('scru', coolerMP1.getOutStream())

recycleLP = recycle('rec1', scrubberLP.getLiquidOutStream())
# separator2.addStream(recycleLP.getOutStream())

mixerLP = mixer('mix1')
mixerLP.addStream(scrubberLP.getGasOutStream())
mixerLP.addStream(separator2.getGasOutStream())

compressorMP1 = compressor('como22', mixerLP.getOutStream(), feedPressure)
coolerMP1 = heater('hett', compressorMP1.getOutStream())
coolerMP1.setOutTemperature(303.0)
scrubberMP1 = separator('scr', coolerMP1.getOutStream())

recycleMP = recycle('rec33', scrubberMP1.getLiquidOutStream())
# separator1.addStream(recycleMP.getOutStream())

mixer1 = mixer('mx32')
mixer1.addStream(scrubberMP1.getGasOutStream())
mixer1.addStream(separator1.getGasOutStream())

# add compressor and set out pressure
compressor1 = compressor('comp44', mixer1.getOutStream(), 60.0)
compressor1.setIsentropicEfficiency(0.8)
cooler1 = heater('coo', compressor1.getOutStream())
cooler1.setOutTemperature(303.0)
compressor2 = compressor('compp2', cooler1.getOutStream(), 120.0)
compressor2.setIsentropicEfficiency(0.77)

runProcess()

print("LPcompressor power ", compressorLP1.getPower() / 1e6, " MW")
print("MPcompressor power ", compressorMP1.getPower() / 1e6, " MW")
print("compressor1 power ", compressor1.getPower() / 1e6, " MW")
print("compressor2 power ", compressor2.getPower() / 1e6, " MW")

print(
    "temperature out of compressor2 ",
    compressor2.getOutStream().getTemperature() - 273.15,
    " °C",
)
#valve1.displayResult()
#separator3.displayResult()
#scrubberLP.displayResult()
# scrubberLP.getLiquidOutStream().displayResult()

# Calculating mechanical design of separators
#separator1.displayResult()
separator1.getMechanicalDesign().setMaxOperationPressure(150.0)
separator1.addSeparatorSection("tray", "")
separator1.getMechanicalDesign().calcDesign()
separator1.getMechanicalDesign().displayResults()
# recycleLP.displayResult()

# separator2.displayResult()
separator2.getMechanicalDesign().setMaxOperationPressure(50.0)
separator2.addSeparatorSection("tray", "")
separator2.getMechanicalDesign().calcDesign()
# separator2.getMechanicalDesign().displayResults();


# separator3.displayResult()
separator3.getMechanicalDesign().setMaxOperationPressure(10.0)
separator3.addSeparatorSection("tray", "")
separator3.getMechanicalDesign().calcDesign()
# separator3.getMechanicalDesign().displayResults();

valve1.getMechanicalDesign().calcDesign()
# valve1.getMechanicalDesign().displayResults();

# phaseenvelope(compressor2.getThermoSystem()).displayResult()
