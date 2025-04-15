from datetime import datetime
import unittest
from hybridheatpumpservice.EConnection import CalculationServiceHybridHeatPump
from dots_infrastructure.DataClasses import SimulatorConfiguration, TimeStepInformation
from dots_infrastructure.test_infra.InfluxDBMock import InfluxDBMock
import helics as h
from esdl.esdl_handler import EnergySystemHandler

from dots_infrastructure import CalculationServiceHelperFunctions


BROKER_TEST_PORT = 23404
START_DATE_TIME = datetime(2024, 1, 1, 0, 0, 0)
SIMULATION_DURATION_IN_SECONDS = 960

def simulator_environment_e_connection():
    return SimulatorConfiguration("EConnection", ["f9502a6a-982b-4df9-98b4-c2c6345267ac"], "Mock-Econnection", "127.0.0.1", BROKER_TEST_PORT, "test-id", SIMULATION_DURATION_IN_SECONDS, START_DATE_TIME, "test-host", "test-port", "test-username", "test-password", "test-database-name", h.HelicsLogLevel.DEBUG, ["PVInstallation", "EConnection"])

class Test(unittest.TestCase):

    def setUp(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_connection
        esh = EnergySystemHandler()
        esh.load_file('test.esdl')
        energy_system = esh.get_energy_system()
        self.energy_system = energy_system

    def test_example(self):
        # Arrange
        service = CalculationServiceHybridHeatPump()
        service.influx_connector = InfluxDBMock()

        weather_params = {}
        weather_params["predicted_solar_irradiances"] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8.333333333333334, 16.666666666666668, 25.0, 33.333333333333336, 59.72222222222223, 86.11111111111111, 112.5, 138.88888888888889, 174.99999999999997, 211.1111111111111, 247.22222222222223, 283.3333333333333, 308.3333333333333, 333.3333333333333, 358.33333333333326, 383.3333333333333, 376.38888888888886, 369.44444444444446, 362.5, 355.55555555555554, 309.72222222222223, 263.8888888888889, 218.0555555555556, 172.22222222222223, 188.19444444444443, 204.16666666666663, 220.13888888888889]
        weather_params["predicted_air_temperatures"] = [284.65, 284.1, 283.54999999999995, 283.0, 282.45, 282.575, 282.7, 282.825, 282.95, 283.075, 283.2, 283.325, 283.45, 283.29999999999995, 283.15, 283.0, 282.85, 282.9, 282.95, 283.0, 283.04999999999995, 283.17499999999995, 283.29999999999995, 283.42499999999995, 283.54999999999995, 284.29999999999995, 285.04999999999995, 285.79999999999995, 286.54999999999995, 287.17499999999995, 287.79999999999995, 288.42499999999995, 289.04999999999995, 289.17499999999995, 289.29999999999995, 289.42499999999995, 289.54999999999995, 289.54999999999995, 289.54999999999995, 289.54999999999995, 289.54999999999995, 289.65, 289.75, 289.85, 289.95, 289.95, 289.95, 289.95]
        weather_params["predicted_soil_temperatures"] = [290.04999999999995, 290.0583333333333, 290.06666666666666, 290.075, 290.0833333333333, 290.09166666666664, 290.1, 290.1083333333333, 290.1166666666666, 290.125, 290.1333333333333, 290.14166666666665, 290.15, 290.1583333333333, 290.16666666666663, 290.17499999999995, 290.18333333333334, 290.19166666666666, 290.2, 290.2083333333333, 290.21666666666664, 290.225, 290.2333333333333, 290.2416666666667, 290.25, 290.24583333333334, 290.2416666666667, 290.23749999999995, 290.2333333333333, 290.22916666666663, 290.225, 290.2208333333333, 290.21666666666664, 290.2125, 290.2083333333333, 290.20416666666665, 290.2, 290.1958333333333, 290.19166666666666, 290.1875, 290.18333333333334, 290.1791666666667, 290.17499999999995, 290.1708333333333, 290.16666666666663, 290.1625, 290.1583333333333, 290.15416666666664]

        service.init_calculation_service(self.energy_system)

        # Execute
        ret_val = service.send_temperatures(weather_params, datetime(2024, 1, 1), TimeStepInformation(1, 2),
                                            "f9502a6a-982b-4df9-98b4-c2c6345267ac", self.energy_system)


if __name__ == '__main__':
    unittest.main()
