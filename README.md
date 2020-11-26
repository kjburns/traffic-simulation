# traffic-simulation
A multimodal road traffic simulator

# Running a Simulation
When starting a simulation, the simulator reads a simulation settings xml file
(defined [here](https://github.com/kjburns/traffic-simulation/blob/develop/xml/simulation-settings.xsd))
which in turn references several other necessary input files, most of which have 
default files available as part of the simulator. These default files can also be
used as starting points for your own refinement:
* vehicle models to be used in the simulation
  * defined [here](https://github.com/kjburns/traffic-simulation/blob/develop/xml/vehicle-models.xsd)
  * default file available [here](https://github.com/kjburns/traffic-simulation/blob/develop/default-files/default.vehicle-models.xml)
* distributions used in the simulation
  * defined [here](https://github.com/kjburns/traffic-simulation/blob/develop/xml/distributions.xsd)
  * depends on vehicle models file
  * default file available [here](https://github.com/kjburns/traffic-simulation/blob/develop/default-files/default.distributions.xml)
* vehicle types & groups used in the simulation
  * a vehicle type is characterized by its distributions of vehicle models used, 
  colors, and occupancy, and by its acceleration and deceleration characteristics--
  these are all defined in the distributions file
  * a vehicle group is a group of vehicle types. These groups are used for other
  aspects of simulation; for example, certain vehicle groups may be banned from
  using a certain lane during certain times of the simulation.
  * defined [here](https://github.com/kjburns/traffic-simulation/blob/develop/xml/vehicle-types.xsd)
  * depends on the vehicle models and distributions files
  * default file available [here](https://github.com/kjburns/traffic-simulation/blob/develop/default-files/default.vehicle-types.xml)
* driving behaviors used in the simulation
  * a driving behavior includes: 
    * car-following behavior, which considers the position of leading and following
    vehicles in determining necessary acceleration. Currently, the car following
    behavior in use is Fritzsche.
    * lane-changing behavior, which considers the vehicle's route and provides for
    free, cooperative, and forced lane changes. Currently, the car following
    behavior in use is Hidas.
    * speed selection behavior, which considers the speed limit and road curvature  
    in selecting the vehicle's desired speed
  * defined [here](https://github.com/kjburns/traffic-simulation/blob/develop/xml/behavior.xsd)
  * default file available [here](https://github.com/kjburns/traffic-simulation/blob/develop/default-files/default.behaviors.xml)
* lane usage in the simulation
  * lanes can be restricted from use by certain vehicle groups.
  * defined [here](https://github.com/kjburns/traffic-simulation/blob/develop/xml/lane-usage.xsd)
  * depends on vehicle types & groups file
  * default file available [here](https://github.com/kjburns/traffic-simulation/blob/develop/default-files/default.lane-usage.xml)
* network file used in the simulation
  * defines network topology and expected vehicle counts
  * there is no default version of this file; it must be defined individually.
  * network file format is defined [here](https://github.com/kjburns/traffic-simulation/blob/develop/xml/network.xsd)
* evaluations
  * This will be defined later.
