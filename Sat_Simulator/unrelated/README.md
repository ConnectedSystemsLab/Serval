For a more detailed overview of the simulator, take a look in GUIDE.md. 

However, here is a quick overview:

In order to run the simulator, you should run example.py (we used python 3.8). In example.py, the objects are loaded and the simulator
is run from our example of IotDevices, RecieveGS, and IotSatellites.

There are configuration options in const.py which indicate certain settings for the simulation such as weather, frequency, and the routing method to use. 

In order to create your own simulation, you should create a new decorator for a satellite and station object. These classes should implement load_data, recieve_packet, and load_packet_buffer. You can see examples of these methods in iotdevice.py, iotSatellite.py, and recieveGS.py and in the documentation in node.py/nodeDecorator.py

When implementing a new constellation, pay attention to the create_link function in links.py. Currently, this is loaded for tinyGS's satellites and ground stations, and will likely not work for what you are trying to implement.

The way that satellites are scheduled is done in routing.py, so take a look there. However, the configuration of which routing method to picked is determined in the const file. 

TODO: Update config const file to JSON/YAML

This is the diagram of the different classes that work here:
![Simulator Diagram](./SatSimulatorFlowDiagram.png)
