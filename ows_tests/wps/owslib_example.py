#!/usr/bin/env python3

from owslib.wps import WebProcessingService, ComplexDataInput

# wps = WebProcessingService('https://rain1.fsv.cvut.cz/services/wps', skip_caps=True)
wps = WebProcessingService('http://localhost:8080/services/wps', skip_caps=True)
processId = 'd-rain-csv'

# 1. test GetCapabilities query
wps.getcapabilities()
print("Test 1: GetCapabilities -> list of processes:")
for process in wps.processes:
    print(process.identifier)

# 2. test DescribeProcess query
process = wps.describeprocess(processId)
print("Test 2: DescribeProcess -> list of parameters:")
for input in process.dataInputs:
    print(input.identifier)
for output in process.processOutputs:
    print(output.identifier)

# 3. test Execute query
print("Test 3: Execute")
with open('test.gml') as f:
    gml_data = ComplexDataInput(f.read())

inputs = [
#    ("input", ComplexDataInput('http://rain.fsv.cvut.cz/geodata/test.gml')),
    ("input", gml_data),
    ("keycolumn", "HLGP_ID"),
    ("return_period", "N2,N5,N10"),
    ("rainlength", "120")
]
execution = wps.execute(processId, inputs)
outputFile = '/tmp/output.csv'
print(execution.getStatus())
execution.getOutput(outputFile)
with open(outputFile) as fd:
    print(fd.readlines())
