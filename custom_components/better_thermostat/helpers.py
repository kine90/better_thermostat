"""Helper functions for the Better Thermostat component."""

import asyncio
import logging
from datetime import datetime
import re
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import device_registry as dr
from homeassistant.components.climate.const import (SERVICE_SET_TEMPERATURE, SERVICE_SET_HVAC_MODE)
from homeassistant.components.number.const import (SERVICE_SET_VALUE)

_LOGGER = logging.getLogger(__name__)


def check_float(potential_float):
	"""Check if a string is a float."""
	try:
		float(potential_float)
		return True
	except ValueError:
		return False


def convert_time(time_string):
	"""Convert a time string to a datetime object."""
	try:
		_current_time = datetime.now()
		_get_hours_minutes = datetime.strptime(time_string, "%H:%M")
		return _current_time.replace(hour=_get_hours_minutes.hour, minute=_get_hours_minutes.minute, second=0, microsecond=0)
	except ValueError:
		return None


def convert_decimal(decimal_string):
	"""Convert a decimal string to a float."""
	try:
		return float(format(float(decimal_string), '.1f'))
	except ValueError:
		return None

async def get_trv_model(self):
	"""Returns the HA device model string"""
	try:
		entity_reg = await er.async_get_registry(self.hass)
		entry = entity_reg.async_get(self.heater_entity_id)
		dev_reg = await dr.async_get_registry(self.hass)
		device = dev_reg.async_get(entry.device_id)
		try:
			return re.search('\((.+?)\)', device.model).group(1)
		except AttributeError:
			return None
	except ValueError:
		return None

async def set_trv_values(self, key, value):
	"""Do necessary actions to set the TRV values."""
	if key == 'temperature':
		await self.hass.services.async_call('climate', SERVICE_SET_TEMPERATURE, {'entity_id': self.heater_entity_id, 'temperature': value}, blocking=True)
		_LOGGER.debug("better_thermostat send %s %s", key, value)
	elif key == 'system_mode':
		await self.hass.services.async_call('climate', SERVICE_SET_HVAC_MODE, {'entity_id': self.heater_entity_id, 'hvac_mode': value}, blocking=True)
		_LOGGER.debug("better_thermostat send %s %s", key, value)
	elif key == 'local_temperature_calibration':
		max_calibration = self.hass.states.get(self.local_temperature_calibration_entity).attributes.get('max')
		min_calibration = self.hass.states.get(self.local_temperature_calibration_entity).attributes.get('min')
		if value > max_calibration:
			value = max_calibration
		if value < min_calibration:
			value = min_calibration
		await self.hass.services.async_call('number', SERVICE_SET_VALUE, {'entity_id': self.local_temperature_calibration_entity, 'value': value}, blocking=True)
		_LOGGER.debug("better_thermostat send %s %s", key, value)
	elif key == 'valve_position':
		await self.hass.services.async_call('number', SERVICE_SET_VALUE, {'entity_id': self.valve_position_entity, 'value': value}, blocking=True)
		_LOGGER.debug("better_thermostat send %s %s", key, value)
	await asyncio.sleep(1)
