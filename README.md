[comment]: # (This file is generated, DO NOT edit this file!)

# Calculation service for esdl_type HybridHeatPump:

This calculation service calculates, sends and updates house and buffer tank temperatures for hybrid heatpump operations based upon the weather data and hybrid heatpump dispatch.

## Calculations

### send_temperatures 

Send the current temperature values for house and buffer tank temperatures depending on the input from the weather service.
#### Input parameters
|Name            |esdl_type            |data_type            |unit            |description            |
|----------------|---------------------|---------------------|----------------|-----------------------|
|solar_irradiance|EnvironmentalProfiles|VECTOR|Wm2|The expected solar irradiance for the coming 12 hours as predicted by the weather service.|
|air_temperature|EnvironmentalProfiles|VECTOR|K|The expected air temperature for the coming 12 hours as predicted by the weather service.|
|soil_temperature|EnvironmentalProfiles|VECTOR|K|The expected soil temperature for the coming 12 hours as predicted by the weather service.|
#### Output values
|Name             |data_type             |unit             |description             |
|-----------------|----------------------|-----------------|------------------------|
|buffer_temperature|DOUBLE|K|The current buffer tank temperature.|
|house_temperatures|VECTOR|K|The current indoor and outdoor temperature of the house.|
### update_temperatures 

Updates the temperature values for house and buffer tank temperatures depending on the input from the weather and energy management system (ems) services.
#### Input parameters
|Name            |esdl_type            |data_type            |unit            |description            |
|----------------|---------------------|---------------------|----------------|-----------------------|
|solar_irradiance|EnvironmentalProfiles|VECTOR|Wm2|The expected solar irradiance for the coming 12 hours as predicted by the weather service.|
|air_temperature|EnvironmentalProfiles|VECTOR|K|The expected air temperature for the coming 12 hours as predicted by the weather service.|
|soil_temperature|EnvironmentalProfiles|VECTOR|K|The expected soil temperature for the coming 12 hours as predicted by the weather service.|
|heat_power_to_buffer_hhp|EConnection|DOUBLE|W|Heat power provided from the hybrid heatpump to the buffer tank as calculated by the ems service.|
|heat_power_to_house_hhp|EConnection|DOUBLE|W|Heat power provided the house as calculated by the ems service.|

### Relevant links
|Link             |description             |
|-----------------|------------------------|
|[HybridHeatPump](https://energytransition.github.io/#router/doc-content/687474703a2f2f7777772e746e6f2e6e6c2f6573646c/HybridHeatPump.html)|Details on the HybridHeatPump esdl type|
|[Space heating demand profiles of districts considering temporal dispersion of thermostat settings in individual buildings](https://doi.org/10.1016/j.buildenv.2022.109839)|Publication describing the space heating demands for a house utilized in this model's calculations.|
|[Modeling a Domestic All-Electric Air-Water Heat-Pump System for Discrete-Time Simulations](https://doi.org/10.1109/UPEC55022.2022.9917983)|Publication describing the heat pump model. The hybrid heat pump model is similar except that the model does not have a tap water buffer.|
