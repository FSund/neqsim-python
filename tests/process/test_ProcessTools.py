# import the package
from neqsim.process.processTools import (compsplitter, waterDewPointAnalyser, hydrateEquilibriumTemperatureAnalyser, virtualstream, clearProcess, newProcess, runProcess, stream, runProcessAsThread, mixer, compressor, recycle2, splitter, valve)
from neqsim.thermo import (TPflash, fluid, printFrame)
from numpy import isnan
from pytest import approx
from jpype.types import *
from neqsim import jNeqSim

def test_compsplitter():
    fluid1 = fluid("srk")  # create a fluid using the SRK-EoS
    fluid1.setTemperature(28.15, "C")
    fluid1.setPressure(100.0, "bara")
    fluid1.addComponent("nitrogen", 1.0, "mol/sec")
    fluid1.addComponent("CO2", 2.3, "mol/sec")
    fluid1.setMixingRule(2)
    clearProcess()
    stream1 = stream(fluid1)
    splittcomp = compsplitter(stream1, [1.0, 0.0])
    runProcess()
    TPflash(splittcomp.getSplitStream(0).getFluid())
    printFrame(splittcomp.getSplitStream(0).getFluid())
    assert splittcomp.getSplitStream(0).getFluid().getViscosity('kg/msec') > 1e-19

def test_waterDewPointAnalyser():
    fluid1 = fluid("srk")  # create a fluid using the SRK-EoS
    fluid1.setTemperature(28.15, "C")
    fluid1.setPressure(100.0, "bara")
    fluid1.addComponent("nitrogen", 1.0, "mol/sec")
    fluid1.addComponent("water", 50e-6, "mol/sec")
    fluid1.setMixingRule(2)
    clearProcess()
    stream1 = stream(fluid1)
    waterDewPoint = waterDewPointAnalyser(stream1)
    runProcess()
    assert waterDewPoint.getMeasuredValue('C') == approx(-11.828217379989212, rel= 0.001)

def test_hydrateEquilibriumTemperatureAnalyser():
    fluid1 = fluid("srk")  # create a fluid using the SRK-EoS
    fluid1.setTemperature(28.15, "C")
    fluid1.setPressure(100.0, "bara")
    fluid1.addComponent("nitrogen", 1.0, "mol/sec")
    fluid1.addComponent("methane", 5, "mol/sec")
    fluid1.addComponent("ethane", 1, "mol/sec")
    fluid1.addComponent("propane", 1, "mol/sec")
    fluid1.addComponent("water", 50e-6, "mol/sec")
    fluid1.setMixingRule(2)
    clearProcess()
    stream1 = stream(fluid1)
    hydrateDewPoint = hydrateEquilibriumTemperatureAnalyser(stream1)
    runProcess()
    assert hydrateDewPoint.getMeasuredValue("C") == approx(-25.204324, rel= 0.001)

def test_runProcessAsThread():
    """
    In the test_runProcessAsThread() we set up a process and run it as a thread. 
    We will start the thread and check that the calculated value is diferent from the final results. 
    Then we set maximum calculation time to 10 sec and finish the calculation and check the results is ok.
    """
    fluid1 = fluid("srk")  # create a fluid using the SRK-EoS
    fluid1.setTemperature(28.15, "C")
    fluid1.setPressure(100.0, "bara")
    fluid1.addComponent("nitrogen", 1.0, "mol/sec")
    fluid1.addComponent("water", 50e-6, "mol/sec")
    fluid1.setMixingRule(2)
    clearProcess()
    stream1 = stream(fluid1)
    waterDewPoint = waterDewPointAnalyser(stream1)
    stream2 = stream(fluid1)
    waterDewPoint2 = waterDewPointAnalyser(stream2)
    stream3 = stream(fluid1)
    waterDewPoint3 = waterDewPointAnalyser(stream3)
    processThread = runProcessAsThread()
    #assert waterDewPoint2.getMeasuredValue('C') != approx(-11.828217379989212, rel= 0.001)
    processThread.join(10000) #max 10 sec calculation time
    assert waterDewPoint2.getMeasuredValue('C') == approx(-11.828217379989212, rel= 0.001)

def test_newprocess():
    fluid1 = fluid("srk")  # create a fluid using the SRK-EoS
    fluid1.setTemperature(28.15, "C")
    fluid1.setPressure(100.0, "bara")
    fluid1.addComponent("nitrogen", 1.0, "mol/sec")
    fluid1.addComponent("CO2", 2.3, "mol/sec")
    fluid1.setMixingRule(2)
    stream1 = stream(fluid1)
    splittcomp = compsplitter(stream1, [1.0, 0.0])
    runProcess()
    newProcess()
    stream1 = stream(fluid1)
    splittcomp = compsplitter(stream1, [1.0, 0.0])
    runProcess()
    TPflash(splittcomp.getSplitStream(0).getFluid())
    #assert splittcomp.getSplitStream(0).getFluid().getViscosity('kg/msec') > 1e-19

def test_flowSplitter():
    temperature_inlet = 35.0
    pressure_inlet = 55.0
    pressure_outlet = 100.0
    gasFlowRate = 5.0 

    fluid1 = fluid('srk')
    fluid1.addComponent("methane", 1.0)

    clearProcess()

    stream1 = stream(fluid1)
    stream1.setPressure(pressure_inlet, 'bara')
    stream1.setTemperature(temperature_inlet, 'C')
    stream1.setFlowRate(gasFlowRate, "MSm3/day")

    streamresycl  = stream(stream1.getFluid().clone())
    streamresycl.setFlowRate(0.1, "MSm3/day")

    mixerStream = mixer()
    mixerStream.addStream(stream1)
    mixerStream.addStream(streamresycl)

    compressor_1 = compressor(mixerStream.getOutletStream(), pressure_outlet)

    stream2 = stream(compressor_1.getOutStream())
    
    streamSplit = splitter(stream2)
    streamSplit.setFlowRates(JDouble[:]([5.0, 0.1]), 'MSm3/day')

    resycStream1 = streamSplit.getSplitStream(1)

    valve1 = valve(resycStream1)
    valve1.setOutletPressure(pressure_inlet, 'bara')

    resycleOp = recycle2()
    resycleOp.addStream(valve1.getOutletStream())
    resycleOp.setOutletStream(streamresycl)
    resycleOp.setFlowAccuracy(1e-4)

    exportStream = stream(streamSplit.getSplitStream(0))
    runProcess()
    assert exportStream.getFlowRate('MSm3/day') == approx(5.0)
    assert streamresycl.getFlowRate('MSm3/day') == approx(0.1)
    
    streamSplit.setFlowRates(JDouble[:]([5, 0.5]), 'MSm3/day')
    runProcess()
    assert exportStream.getFlowRate('MSm3/day') == approx(5.0)
    assert streamresycl.getFlowRate('MSm3/day') == approx(0.5)

    streamSplit.setFlowRates(JDouble[:]([-1, 2.5]), 'MSm3/day')
    runProcess()
    assert exportStream.getFlowRate('MSm3/day') == approx(5.0)
    assert streamresycl.getFlowRate('MSm3/day') == approx(2.5)

    streamSplit.setSplitFactors(JDouble[:]([1.0, 0.0]))
    runProcess()
    assert exportStream.getFlowRate('MSm3/day') == approx(5.0)
    assert streamresycl.getFlowRate('MSm3/day') == approx(0.0)

  

def test_virtualstream():
    fluid1 = fluid('srk')
    fluid1.addComponent("methane", 1.0)

    clearProcess()
    stream1 = stream(fluid1)
    stream1.setFlowRate(3.1, "MSm3/day")
    vstream = virtualstream(stream1)
    vstream.setFlowRate(1.1, "MSm3/day")
    vstream.setTemperature(25.0, 'C')
    vstream.setPressure(25.0, 'bara')
    runProcess()
    assert stream1.getFlowRate('MSm3/day') == approx(3.1)
    assert vstream.getOutStream().getFlowRate('MSm3/day') == approx(1.1)

# Example of a method using direct calls to neqsim java
def testNoUseOfThermosOrProcessTools():
    fluid = jNeqSim.thermo.system.SystemSrkEos((273.15 + 25.0), 10.00)
    fluid.addComponent("methane", 0.900)
    fluid.addComponent("ethane", 0.100)
    fluid.addComponent("n-heptane", 1.00)
    fluid.setMixingRule(2)

    stream1 = jNeqSim.processSimulation.processEquipment.stream.Stream("Stream1", fluid)
    stream1.setPressure(10.0, 'bara')
    stream1.setTemperature(25.0, 'C')
    stream1.setFlowRate(50.0, 'kg/hr')

    valve1 = jNeqSim.processSimulation.processEquipment.valve.ThrottlingValve("valve_1", stream1)
    valve1.setOutletPressure(5.0, 'bara')

    separator1 = jNeqSim.processSimulation.processEquipment.separator.Separator("sep 1")
    separator1.addStream(valve1.getOutStream())

    operation = jNeqSim.processSimulation.processSystem.ProcessSystem()
    operation.add(stream1)
    operation.add(valve1)
    operation.add(separator1)

    operation.run()
    
    print('temperature ', operation.getUnit('sep 1').getGasOutStream().getTemperature('C'))
    assert operation.getUnit('sep 1').getGasOutStream().getFlowRate('kg/hr') == approx(7.580303857)