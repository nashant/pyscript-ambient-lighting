from typing import List, Any
import json

from . import utils

class AmbiLight():

    def __init__(
        self,
        id: str,
        name: str,
        friendly_name: str,
        light_id: str,
        lux_sensor_id: str,
        lux_target_id: str,
        motion_sensor_id: str,
        lux_minimum: int=None,
        lux_maximum: int=None,
        polynomial_lux: List[float]=None,
        polynomial_brightness: List[float]=None
    ):
        self._id = id
        self._entity = self._get_or_init(id)

        self._setattr('name', name)
        self._setattr('friendly_name', friendly_name)
        self._setattr('light_id', light_id)
        self._setattr('lux_sensor_id', lux_sensor_id)
        self._setattr('lux_target_id', lux_target_id)
        self._setattr('motion_sensor_id', motion_sensor_id)
        if lux_minimum != None: self._setattr('lux_minimum', lux_minimum)
        if lux_maximum != None: self._setattr('lux_maximum', lux_maximum)
        if polynomial_lux != None: self._setattr('polynomial_lux', polynomial_lux)
        if polynomial_brightness != None: self._setattr('polynomial_brightness', polynomial_brightness)

        self._triggers = {}

        if None not in [lux_minimum, lux_maximum, polynomial_lux, polynomial_brightness]:
            self._setup_triggers()

    def _setattr(self, attribute: str, value: Any):
        state.setattr(f"{self._id}.{attribute}", value)

    def _get_or_init(self, id):
        if id not in state.names('pyscript'): state.persist(id, 'off')
        return state.get(id)

    def lux_to_brightness(self, lux: int):
        return utils.convert_lux(lux, *self._entity.polynomial_lux)

    def brightness_to_lux(self, brightness: int):
        return utils.convert_lux(brightness, *self._entity.polynomial_brightness)

    def _setup_triggers(self):
        al = self._entity

        @time_trigger('startup')
        @state_trigger(f"{al.light_id}.brightness")
        def update_light_lux(value=None):

            light = state.get(al.light_id)
            light_lux = round(self.brightness_to_lux(light.brightness)) if value == 'on' else 0

            self._setattr('light_lux', light_lux)

        @state_trigger(f"{al.lux_sensor_id} != {al.lux_sensor_id}.old", al.lux_target_id)
        def update_target_brightness(var_name=None, value=None):
            if 'light_lux' not in state.getattr(self._id):
                log.info(f"light_lux not yet set for {self._id}, try changing the light brightness")
                return

            ambilight = state.get(self._id)
            target_lux = value if var_name == ambilight.lux_target_id else state.get(ambilight.lux_target_id)
            current_lux = value if var_name == ambilight.lux_sensor_id else state.get(ambilight.lux_sensor_id)
            light_lux = ambilight.light_lux

            if float(current_lux) == float(target_lux):
                log.debug(f"Taget lux reached for {self._id}")
                return

            log.debug(f"Triggered by {var_name}, target_lux: {target_lux}, current_lux: {current_lux}, light_lux: {light_lux}")

            ambient_lux = int( float(current_lux) - float(light_lux) )
            log.debug(f"Ambient lux for {ambilight.lux_sensor_id} is {ambient_lux}lx")

            required_lux = int(float(target_lux)) - ambient_lux
            required_brightness = int(self.lux_to_brightness(required_lux))
            log.debug(f"Lux required from {ambilight.light_id} is {required_lux}lx, brightness of {required_brightness}")

            target_brightness = min([ max([ required_brightness, 0 ]), 254 ])

            try: current_target = ambilight.target_brightness
            except: current_target = -1

            if current_target != target_brightness:
                log.debug(f"Setting target brightness for {ambilight.light_id} to {target_brightness}")
                state.setattr(f"{self._id}.target_brightness", target_brightness)
            else:
                log.debug(f"Target brightness for {ambilight.light_id} has not changed from {target_brightness}")

        @time_trigger('period(now, 30s)')
        @state_trigger(f"{self._id}.target_brightness", al.motion_sensor_id)
        def light_trigger(var_name=None, value=None):
            if 'target_brightness' not in state.getattr(self._id):
                log.debug(f"target_brightness not yet set for {self._id}")
                return

            ambilight = state.get(self._id)
            if ambilight == 'off':
                log.debug(f"Ambilight {self._id} is off, doing nothing")
                return

            occupied = state.get(ambilight.motion_sensor_id) == 'on'
            light_on = state.get(ambilight.light_id) == 'on'

            target_brightness = int(ambilight.target_brightness)
            lux_from_target_brightness = self.brightness_to_lux(target_brightness)

            if not occupied:
                if light_on:
                    light.turn_off(entity_id=ambilight.light_id)
                else:
                    return
            elif target_brightness == 0:
                light.turn_off(entity_id=ambilight.light_id)
            else:
                transition = 20 if light_on else 2
                light.turn_on(entity_id=ambilight.light_id, brightness=target_brightness, transition=transition)

        self._triggers['update_light_lux'] = update_light_lux
        self._triggers['update_target_brightness'] = update_target_brightness
        self._triggers['light_trigger'] = light_trigger