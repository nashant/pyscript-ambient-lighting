from . import utils

def convert_lux(x, a, b, c, d, e):
    return a * x + b * x**2 + c * x**3 + d * x**4 + e


#@service
#def check_lux_conversion(light_id=None, input_type=None, value=None):
#    """yaml
#    name: Check the conversion between light pct and lux level
#    description: |
#        This tests the polynomial function values calculated by pyscript.calculate_lux_polynomials
#    fields:
#        light_id:
#            description: The entity_id of the light to test
#            example: light.office
#            required: true
#            selector:
#                entity:
#                    domain: light
#        input_type:
#            description: Convert from lux or light brightness?
#            example: lux
#            required: true
#            selector:
#                select:
#                    options:
#                    - lux
#                    - brightness
#        value:
#            description: The number to convert
#            example: 30
#            required: true
#            selector:
#                number:
#                   start: 0
#                   end: 254
#    """
#    attrs = state.getattr(light_id)
#    poly = [ float(n) for n in attrs[f"{input_type}_poly"] ]
#    out = round(convert_lux(value, *poly), 0)
#    output_type = 'lux' if input_type == 'brightness' else 'brightness'
#    persistent_notification.create(message=f"{output_type} is {out} at {input_type} {value}")


#@service
#def setup_ambilight_entity(name: str, light_id: str, sensor_id: str, target_lux_id: str, motion_sensor_id: str):
#    """yaml
#    name: Set up Ambient Lighting
#    description: |
#        This will set up an Ambient Lighting entity.
#        It will gather the lux levels at 5% increments of brightness.
#        It is recommended that you block out all other light sources while running this.
#    fields:
#        name:
#            name: Name
#            description: Name of the Ambilight entity
#            example: Office Ambilight
#            required: true
#            selector:
#                text:
#        light_id:
#            name: Light entity
#            description: The entity_id of the light to test
#            example: light.office
#            required: true
#            selector:
#                entity:
#                    domain: light
#        lux_sensor_id:
#            name: Lux sensor entity
#            description: The entity_id of the lux sensor to use
#            example: sensor.office_lux
#            required: true
#            selector:
#                entity:
#                    domain: sensor
#                    device_class: illuminance
#        target_lux_id:
#            name: Lux target entity
#            description: Input Number entity which defines the target lux
#            example: input_number.office_lux_min
#            required: true
#            selector:
#                entity:
#                    domain: input_number
#        motion_sensor_id:
#            name: Motion sensor entity
#            description: The entity_id of the motion sensor to tie to the ambilight
#            example: binary_sensor.office_motion
#            required: true
#            selector:
#                entity:
#                    domain: binary_sensor
#                    device_class: motion
#    """
#    log.info("setup_ambilight_entity")
#    entity_id = f"pyscript.{name.lower().replace(' ', '_')}"
#    if entity_id in state.names('pyscript'):
#        persistent_notification.create(message=f"The entity {entity_id} is already set up")
#        return
#
#    try:
#        lux, brightness, minimum, maximum = update_ambilight_polynomials(entity_id, light_id, sensor_id)
#        values = {
#            'light_id': light_id,
#            'lux_sensor_id': sensor_id,
#            'target_lux_id': target_lux_id,
#            'motion_sensor_id': motion_sensor_id,
#            'friendly_name': name,
#            'lux_minimum': minimum,
#            'lux_maximum': maximum,
#            'polynomial_lux': lux,
#            'polynomial_brightness': brightness
#        }
#        state.persist(entity_id, 'off', values)
#        persistent_notification.create(message=f"{name} set up successfully")
#    except Exception as e:
#        persistent_notification.create(message=f"Unable to set up {name}")
#        log.error(e)


@service
def update_ambilight_polynomials(entity_id: str):
    """yaml
    name: Update Ambilight polynomials
    description: This re-runs the set-up stage and calculations for the lux polynomial functions
    fields:
        entity_id:
            name: Entity
            example: pyscript.office_ambilight
            required: true
            selector:
                entity:
                    domain: pyscript
    """
    log.debug("update_ambilight_polynomials")
    ambilight = state.get(entity_id)
    try:
        levels = utils.gather_lux_levels(ambilight.light_id, ambilight.lux_sensor_id)
        log.debug(f"Lux levels gathered for {entity_id}")
    except Exception as e:
        persistent_notification.create(message=f"Unable to gather lux levels for {entity_id}")
        raise(e)

    try: 
        levels[0], levels[1] = utils.get_polynomials(levels[0], levels[1])
        log.debug(f"Got polynomials for {entity_id}")
    except Exception as e:
        persistent_notification.create(message=f"Unable to query polynomials for {entity_id}")
        raise(e)

    try:
        state.setattr(f"{entity_id}.lux_minimum", levels[2])
        state.setattr(f"{entity_id}.lux_maximum", levels[3])
        state.setattr(f"{entity_id}.polynomial_lux", levels[0])
        state.setattr(f"{entity_id}.polynomial_brightness", levels[1])
        persistent_notification.create(message=f"Lux levels updated for {entity_id}")
    except:
        persistent_notification.create(message=f"Unable to save attributes for {entity_id}")


@service
def set_ambilight_attribute(entity_id: str, attribute: str, value: str):
    """yaml
    name: Set an Ambilight attribute
    description: Set an attribute for an ambilight
    fields:
        entity_id:
            name: Entity
            example: pyscript.office_ambilight
            required: true
            selector:
                entity:
                    domain: pyscript
        attribute:
            name: Attribute
            example: attribute
            required: true
            selector:
                text:
        value:
            name: Value
            example: value
            required: true
            selector:
                text:
    """
    state.setattr(f"{entity_id}.{attribute}", value)


#@service
#def delete_ambilight_attribute(entity_id: str, attribute: str, value: str):
#    """yaml
#    name: Delete an Ambilight attribute
#    description: Delete an attribute from an ambilight entity
#    fields:
#        entity_id:
#            name: Entity
#            example: pyscript.office_ambilight
#            required: true
#            selector:
#                entity:
#                    domain: pyscript
#        attribute:
#            name: Attribute
#            example: attribute
#            required: true
#            selector:
#                text:
#    """
#    state.delete(f"{entity_id}.{attribute}")


@service
def delete_ambilight_entity(entity_id: str):
    """yaml
    name: Delete Ambient Lighting entity
    description: Delete an Ambient Lighting entity.
    fields:
        entity_id:
            name: Entity
            example: pyscript.office_ambilight
            required: true
            selector:
                entity:
                    domain: pyscript
    """
    state.delete(entity_id)


@service
def enable_ambilight(entity_id: str):
    """yaml
    name: Enable an Ambient Lighting entity
    description: Enable an Ambient Lighting entity.
    fields:
        entity_id:
            name: Entity
            example: pyscript.office_ambilight
            required: true
            selector:
                entity:
                    domain: pyscript
    """
    state.set(entity_id, 'on')


@service
def disable_ambilight(entity_id: str):
    """yaml
    name: Disable an Ambient Lighting entity
    description: Disable an Ambient Lighting entity.
    fields:
        entity_id:
            name: Entity
            example: pyscript.office_ambilight
            required: true
            selector:
                entity:
                    domain: pyscript
    """
    state.set(entity_id, 'off')


@service
def toggle_ambilight(entity_id: str):
    """yaml
    name: Toggle an Ambient Lighting entity
    description: Toggle an Ambient Lighting entity.
    fields:
        entity_id:
            name: Entity
            example: pyscript.office_ambilight
            required: true
            selector:
                entity:
                    domain: pyscript
    """
    to_state = 'on' if state.get(entity_id) == 'off' else 'off'
    state.set(entity_id, to_state)