# -*- coding: utf-8 -*-
from datetime import datetime
from esdl import esdl
import helics as h
from dots_infrastructure.DataClasses import EsdlId, HelicsCalculationInformation, PublicationDescription, SubscriptionDescription, TimeStepInformation, TimeRequestType
from dots_infrastructure.HelicsFederateHelpers import HelicsSimulationExecutor
from dots_infrastructure.Logger import LOGGER
from esdl import EnergySystem
from dots_infrastructure.CalculationServiceHelperFunctions import get_single_param_with_name

import json
import numpy as np
from hybridheatpumpservice.thermalsystems import House, HeatBuffer

class CalculationServiceHybridHeatPump(HelicsSimulationExecutor):

    def __init__(self):
        super().__init__()

        subscriptions_values = [
            SubscriptionDescription(esdl_type="EnvironmentalProfiles",
                                   input_name="solar_irradiance",
                                   input_unit="Wm2",
                                   input_type=h.HelicsDataType.VECTOR),
            SubscriptionDescription(esdl_type="EnvironmentalProfiles",
                                   input_name="air_temperature",
                                   input_unit="K",
                                   input_type=h.HelicsDataType.VECTOR),
            SubscriptionDescription(esdl_type="EnvironmentalProfiles",
                                   input_name="soil_temperature",
                                   input_unit="K",
                                   input_type=h.HelicsDataType.VECTOR)
        ]

        publication_values = [
            PublicationDescription(global_flag=True,
                                   esdl_type="HybridHeatPump",
                                   output_name="buffer_temperature",
                                   output_unit="K",
                                   data_type=h.HelicsDataType.DOUBLE),
            PublicationDescription(global_flag=True,
                                   esdl_type="HybridHeatPump",
                                   output_name="house_temperatures",
                                   output_unit="K",
                                   data_type=h.HelicsDataType.VECTOR)
        ]

        hybridheatpump_period_in_seconds = 900
        self.hybridheatpump_period_in_seconds = hybridheatpump_period_in_seconds

        calculation_information = HelicsCalculationInformation(
            time_period_in_seconds=hybridheatpump_period_in_seconds,
            offset=0, 
            uninterruptible=False, 
            wait_for_current_time_update=False, 
            terminate_on_error=True, 
            calculation_name="send_temperatures",
            inputs=subscriptions_values, 
            outputs=publication_values, 
            calculation_function=self.send_temperatures
        )
        self.add_calculation(calculation_information)

        subscriptions_values = [
            SubscriptionDescription(esdl_type="EnvironmentalProfiles",
                                   input_name="solar_irradiance",
                                   input_unit="Wm2",
                                   input_type=h.HelicsDataType.VECTOR),
            SubscriptionDescription(esdl_type="EnvironmentalProfiles",
                                   input_name="air_temperature",
                                   input_unit="K",
                                   input_type=h.HelicsDataType.VECTOR),
            SubscriptionDescription(esdl_type="EnvironmentalProfiles",
                                   input_name="soil_temperature",
                                   input_unit="K",
                                   input_type=h.HelicsDataType.VECTOR),
            SubscriptionDescription(esdl_type="EConnection",
                                    input_name="heat_power_to_buffer_hhp",
                                    input_unit="W",
                                    input_type=h.HelicsDataType.DOUBLE),
            SubscriptionDescription(esdl_type="EConnection",
                                    input_name="heat_power_to_house_hhp",
                                    input_unit="W",
                                    input_type=h.HelicsDataType.DOUBLE)
        ]

        hybridheatpump_update_period_in_seconds = 900

        calculation_information_update = HelicsCalculationInformation(hybridheatpump_update_period_in_seconds, 0, False, False, True, "update_temperatures", subscriptions_values, [], self.update_temperatures)
        self.add_calculation(calculation_information_update)

    def init_calculation_service(self, energy_system: esdl.EnergySystem):
        LOGGER.info("init calculation service")
        self.hhp_description_dicts: dict[EsdlId, dict[str, float]] = {}
        self.hhp_esdl_thermalpower: dict[EsdlId, float] = {}

        self.heat_buffers: dict[EsdlId, HeatBuffer] = {}
        self.houses: dict[EsdlId, House] = {}

        self.inv_capacitance_matrices: dict[EsdlId, np.array] = {}
        self.conductance_matrices: dict[EsdlId, np.array] = {}
        self.forcing_matrices: dict[EsdlId, np.array] = {}

        for esdl_id in self.simulator_configuration.esdl_ids:
            LOGGER.info(f"Example of iterating over esdl ids: {esdl_id}")
            # Initialize heat tanks and houses
            # Get data from ESDL
            for obj in energy_system.eAllContents():
                if hasattr(obj, "id") and obj.id == esdl_id:
                    hhpsystem = obj
                    if isinstance(obj.eContainer(), esdl.Building):
                        building_description = json.loads(obj.eContainer().description)
            self.hhp_description_dicts[esdl_id] = json.loads(hhpsystem.description)
            self.hhp_esdl_thermalpower[esdl_id] = hhpsystem.heatPumpThermalPower

            # Set Buffer Tank
            buffer_capacitance = self.hhp_description_dicts[esdl_id]['buffer_capacitance']
            self.heat_buffers[esdl_id] = HeatBuffer(buffer_capacitance)

            # Set Houses
            capacities = {'C_in': building_description['C_in'], 'C_out': building_description['C_out']}
            resistances = {'R_exch': building_description['R_exch'], 'R_floor': building_description['R_floor'],
                           'R_vent': building_description['R_vent'], 'R_cond': building_description['R_cond']}
            window_area = building_description['A_glass']
            self.houses[esdl_id] = House(capacities, resistances, window_area)


    def send_temperatures(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        # START user calc
        LOGGER.info("calculation 'send_temperatures' started")

        predicted_solar_irradiances = get_single_param_with_name(param_dict, "solar_irradiance")
        predicted_air_temperatures = get_single_param_with_name(param_dict, "air_temperature")
        predicted_soil_temperatures = get_single_param_with_name(param_dict, "soil_temperature")

        # Check if the house and tank temperatures are properly initialized
        house = self.houses[esdl_id]
        heat_buffer = self.heat_buffers[esdl_id]
        if (house.temperatures is None) or (heat_buffer.temperature is None):
            current_solar_irradiance = predicted_solar_irradiances[0]
            current_air_temperature  = predicted_air_temperatures[0]
            current_soil_temperature = predicted_soil_temperatures[0]

            hhp_description_dict = self.hhp_description_dicts[esdl_id]

            heat_buffer.set_initial_temperature(hhp_description_dict['buffer_temp_0'])
            house.set_initial_temperatures(hhp_description_dict['house_temp_0'],
                                           self.hhp_esdl_thermalpower[esdl_id],
                                           current_air_temperature,
                                           current_soil_temperature,
                                           current_solar_irradiance)

            self.heat_buffers[esdl_id] = heat_buffer
            self.houses[esdl_id] = house

            house_temperatures_list = house.temperatures.tolist()
        else:
            house_temperatures_list = house.temperatures



        ret_val = {}
        ret_val["buffer_temperature"]   = heat_buffer.temperature
        ret_val["house_temperatures"]   = house_temperatures_list

        LOGGER.debug(heat_buffer.temperature, house.temperatures)

        LOGGER.info("calculation 'send_temperatures' finished")
        # END user calc
        return ret_val
    
    def update_temperatures(self, param_dict : dict, simulation_time : datetime, time_step_number : TimeStepInformation, esdl_id : EsdlId, energy_system : EnergySystem):
        # START user calc
        LOGGER.info("calculation 'update_temperatures' started")
        predicted_solar_irradiances = get_single_param_with_name(param_dict, "solar_irradiance")
        predicted_air_temperatures = get_single_param_with_name(param_dict, "air_temperature")
        predicted_soil_temperatures = get_single_param_with_name(param_dict, "soil_temperature")
        heat_to_buffer = get_single_param_with_name(param_dict, "heat_power_to_buffer_hhp")
        heat_to_house = get_single_param_with_name(param_dict,"heat_power_to_house_hhp")

        current_air_temperature = predicted_air_temperatures[0]
        current_soil_temperature = predicted_soil_temperatures[0]
        current_solar_irradiance = predicted_solar_irradiances[0]

        heat_buffer = self.heat_buffers[esdl_id]
        house = self.houses[esdl_id]

        LOGGER.info(f"esdl id: {esdl_id}")
        LOGGER.info(f"house temperatures before: {house.temperatures}")
        LOGGER.info(f"buffer temperature before: {heat_buffer.temperature}")
        LOGGER.info(f"heat to house: {heat_to_house}")
        LOGGER.info(f"heat to buffer: {heat_to_buffer}")

        # Update temperatures
        house.update_temperatures(self.hybridheatpump_period_in_seconds,
                                  current_air_temperature,
                                  current_soil_temperature,
                                  current_solar_irradiance,
                                  heat_to_house)
        heat_buffer.update_temperature(self.hybridheatpump_period_in_seconds,
                                       heat_to_house,
                                       heat_to_buffer)

        LOGGER.info(f"house temperatures after: {house.temperatures}")
        LOGGER.info(f"buffer temperature after: {heat_buffer.temperature}")

        house_temperatures = house.temperatures
        heat_buffer_temperature = heat_buffer.temperature

        # Check whether temperatures did not surpass the limits due to some numerical error
        lower_bound_buffer = self.hhp_description_dicts[esdl_id]['buffer_temp_min']
        upper_bound_buffer = self.hhp_description_dicts[esdl_id]['buffer_temp_max']
        lower_bound_house = self.hhp_description_dicts[esdl_id]['house_temp_min']

        # Correct errors up till error eps
        eps = 1.0e-4
        if abs(heat_buffer_temperature - lower_bound_buffer) < eps:
            heat_buffer_temperature = lower_bound_buffer + eps
        if abs(heat_buffer_temperature - upper_bound_buffer) < eps:
            heat_buffer_temperature = upper_bound_buffer - eps
        if abs(house_temperatures[0] - lower_bound_house) < eps:
            house_temperatures[0] = lower_bound_house + eps

        # Raise errors if the values are still not within boundaries
        if (heat_buffer_temperature < lower_bound_buffer) or (heat_buffer_temperature > upper_bound_buffer):
            raise ValueError(
                f"Hybrid Heat pump {esdl_id} is charged over/under its buffer capacity")
        if house_temperatures[0] < lower_bound_house:
            LOGGER.info(
                f"Hybrid Heat pump {esdl_id} is charged over/under its house capacity")
            raise ValueError(
                f"Hybrid Heat pump {esdl_id} is charged over/under its house capacity")

        # Save as state
        house.temperatures = house_temperatures.tolist()
        heat_buffer.temperature = heat_buffer_temperature
        self.houses[esdl_id] = house
        self.heat_buffers[esdl_id] = heat_buffer

        self.influx_connector.set_time_step_data_point(esdl_id, 'buffer_temperature',
                                                      simulation_time, heat_buffer_temperature)
        self.influx_connector.set_time_step_data_point(esdl_id, 'house_temperature',
                                                      simulation_time, house_temperatures[0])
        LOGGER.info("calculation 'update_temperatures' finished")
        # ret_val = {}
        return None

if __name__ == "__main__":

    helics_simulation_executor = CalculationServiceHybridHeatPump()
    helics_simulation_executor.start_simulation()
    helics_simulation_executor.stop_simulation()
