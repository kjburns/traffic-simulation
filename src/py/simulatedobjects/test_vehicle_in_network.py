import unittest
from py.simulatedobjects.vehicle_in_network import VehicleInNetwork

class TestVehicleInNetwork(unittest.TestCase):
    def test_that_ids_are_as_expected(self):
        VEHICLE_COUNT = 20

        vehicles: list = [VehicleInNetwork() for _ in range(VEHICLE_COUNT)]

        # must start with 0
        self.assertEqual(vehicles[0].id, 0)

        # must be sequential
        self.assertListEqual(list(map(lambda veh: veh.id, vehicles)), list(range(VEHICLE_COUNT)))

        # each value must be unique
        self.assertEqual(len(set(map(lambda veh: veh.id, vehicles))), VEHICLE_COUNT)
    pass

if (__name__ == '__main__'):
    unittest.main()