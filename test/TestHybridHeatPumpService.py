from datetime import datetime
import unittest
import helics as h
from dots_infrastructure.DataClasses import SimulatorConfiguration, TimeStepInformation
from dots_infrastructure.test_infra.InfluxDBMock import InfluxDBMock
from dots_infrastructure import CalculationServiceHelperFunctions
from esdl.esdl_handler import EnergySystemHandler

from hybridheatpumpservice.hybrid_heatpump_service import CalculationServiceHybridHeatPump


BROKER_TEST_PORT = 23404
START_DATE_TIME = datetime(2024, 1, 1, 0, 0, 0)
SIMULATION_DURATION_IN_SECONDS = 960

def simulator_environment_e_connection():
    return SimulatorConfiguration("EConnection", ["ad579719-bbf4-425e-86f1-42f5afa0a7fd"], "Mock-Econnection", "127.0.0.1", BROKER_TEST_PORT, "test-id", SIMULATION_DURATION_IN_SECONDS, START_DATE_TIME, "test-host", "test-port", "test-username", "test-password", "test-database-name", h.HelicsLogLevel.DEBUG, ["PVInstallation", "EConnection"])

class Test(unittest.TestCase):

    def setUp(self):
        CalculationServiceHelperFunctions.get_simulator_configuration_from_environment = simulator_environment_e_connection
        esh = EnergySystemHandler()
        esh.load_file('test/test.esdl')
        energy_system = esh.get_energy_system()
        self.energy_system = energy_system

    def test_send_temperatures(self):
        # Arrange
        service = CalculationServiceHybridHeatPump()
        service.influx_connector = InfluxDBMock()

        weather_params = {}
        weather_params["solar_irradiance"] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8.333333333333334, 16.666666666666668, 25.0, 33.333333333333336, 59.72222222222223, 86.11111111111111, 112.5, 138.88888888888889, 174.99999999999997, 211.1111111111111, 247.22222222222223, 283.3333333333333, 308.3333333333333, 333.3333333333333, 358.33333333333326, 383.3333333333333, 376.38888888888886, 369.44444444444446, 362.5, 355.55555555555554, 309.72222222222223, 263.8888888888889, 218.0555555555556, 172.22222222222223, 188.19444444444443, 204.16666666666663, 220.13888888888889]
        weather_params["air_temperature"] = [279.25, 279.54999999999995, 279.85, 280.15, 280.45, 280.7, 280.95, 281.2,
                                            281.45, 281.775, 282.1, 282.42499999999995, 282.75, 282.85, 282.95,
                                            283.04999999999995, 283.15, 283.15, 283.15, 283.15, 283.15, 282.95, 282.75,
                                            282.54999999999995, 282.35, 282.275, 282.2, 282.125, 282.04999999999995,
                                            282.125, 282.2, 282.275, 282.35, 282.375, 282.4, 282.42499999999995, 282.45,
                                            282.375, 282.29999999999995, 282.225, 282.15, 282.025, 281.9, 281.775,
                                            281.65, 281.625, 281.6, 281.575]
        weather_params["soil_temperature"] = [281.3833333333333, 281.37916666666666, 281.375, 281.37083333333334,
                                             281.3666666666666, 281.36249999999995, 281.3583333333333,
                                             281.35416666666663, 281.35, 281.3458333333333, 281.34166666666664,
                                             281.3375, 281.3333333333333, 281.32916666666665, 281.325,
                                             281.3208333333333, 281.31666666666666, 281.3125, 281.30833333333334,
                                             281.3041666666666, 281.29999999999995, 281.2958333333333,
                                             281.29166666666663, 281.2875, 281.2833333333333, 281.27916666666664,
                                             281.275, 281.2708333333333, 281.26666666666665, 281.2625,
                                             281.2583333333333, 281.25416666666666, 281.25, 281.24583333333334,
                                             281.2416666666666, 281.23749999999995, 281.2333333333333,
                                             281.22916666666663, 281.225, 281.2208333333333, 281.21666666666664,
                                             281.2125, 281.2083333333333, 281.20416666666665, 281.2, 281.1958333333333,
                                             281.19166666666666, 281.1875]

        service.init_calculation_service(self.energy_system)

        # Execute
        ret_val = service.send_temperatures(weather_params, datetime(2024, 1, 1), TimeStepInformation(1, 2),
                                            "ad579719-bbf4-425e-86f1-42f5afa0a7fd", self.energy_system)
        
        # Assert
        expected_buffer_temperature = 315.93853596915767
        expected_indoor_temperature = 291.8432403998079
        expected_outdoor_temperature = 289.5683667517938
        # self.assertAlmostEqual(ret_val["buffer_temperature"], expected_buffer_temperature)
        # self.assertAlmostEqual(ret_val["house_temperatures"][0], expected_indoor_temperature)
        # self.assertAlmostEqual(ret_val["house_temperatures"][1], expected_outdoor_temperature)

    def test_update_temperatures(self):
        # Arrange
        service = CalculationServiceHybridHeatPump()
        service.influx_connector = InfluxDBMock()

        input_params = {}
        input_params["solar_irradiance"] = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 8.333333333333334, 16.666666666666668, 25.0, 33.333333333333336, 59.72222222222223, 86.11111111111111, 112.5, 138.88888888888889, 174.99999999999997, 211.1111111111111, 247.22222222222223, 283.3333333333333, 308.3333333333333, 333.3333333333333, 358.33333333333326, 383.3333333333333, 376.38888888888886, 369.44444444444446, 362.5, 355.55555555555554, 309.72222222222223, 263.8888888888889, 218.0555555555556, 172.22222222222223, 188.19444444444443, 204.16666666666663, 220.13888888888889]
        input_params["air_temperature"] = [279.25, 279.54999999999995, 279.85, 280.15, 280.45, 280.7, 280.95, 281.2,
                                            281.45, 281.775, 282.1, 282.42499999999995, 282.75, 282.85, 282.95,
                                            283.04999999999995, 283.15, 283.15, 283.15, 283.15, 283.15, 282.95, 282.75,
                                            282.54999999999995, 282.35, 282.275, 282.2, 282.125, 282.04999999999995,
                                            282.125, 282.2, 282.275, 282.35, 282.375, 282.4, 282.42499999999995, 282.45,
                                            282.375, 282.29999999999995, 282.225, 282.15, 282.025, 281.9, 281.775,
                                            281.65, 281.625, 281.6, 281.575]
        input_params["soil_temperature"] = [281.3833333333333, 281.37916666666666, 281.375, 281.37083333333334,
                                             281.3666666666666, 281.36249999999995, 281.3583333333333,
                                             281.35416666666663, 281.35, 281.3458333333333, 281.34166666666664,
                                             281.3375, 281.3333333333333, 281.32916666666665, 281.325,
                                             281.3208333333333, 281.31666666666666, 281.3125, 281.30833333333334,
                                             281.3041666666666, 281.29999999999995, 281.2958333333333,
                                             281.29166666666663, 281.2875, 281.2833333333333, 281.27916666666664,
                                             281.275, 281.2708333333333, 281.26666666666665, 281.2625,
                                             281.2583333333333, 281.25416666666666, 281.25, 281.24583333333334,
                                             281.2416666666666, 281.23749999999995, 281.2333333333333,
                                             281.22916666666663, 281.225, 281.2208333333333, 281.21666666666664,
                                             281.2125, 281.2083333333333, 281.20416666666665, 281.2, 281.1958333333333,
                                             281.19166666666666, 281.1875]

        input_params["heat_power_to_buffer_hhp"] = 20
        input_params["heat_power_to_house_hhp"] = 4000

        service.init_calculation_service(self.energy_system)

        # Execute
        service.send_temperatures(input_params, datetime(2024, 1, 1), TimeStepInformation(1, 2), "ad579719-bbf4-425e-86f1-42f5afa0a7fd", self.energy_system)
        service.update_temperatures(input_params, datetime(2024, 1, 1), TimeStepInformation(1, 2), "ad579719-bbf4-425e-86f1-42f5afa0a7fd", self.energy_system)
        
        # Assert
        saved_datapoints = service.influx_connector.data_points
        expected_buffer_temperature = 315.93853596915767
        expected_house_temperature = 291.75932454471314
        calculated_buffer_temperature = saved_datapoints[0].value
        calculated_house_temperature = saved_datapoints[1].value
        # self.assertAlmostEqual(expected_buffer_temperature, calculated_buffer_temperature)
        # self.assertAlmostEqual(expected_house_temperature, calculated_house_temperature)



if __name__ == '__main__':
    unittest.main()
