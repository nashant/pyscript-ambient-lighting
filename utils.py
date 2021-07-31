def convert_lux(x: int, a: float, b: float, c: float, d: float, e: float):
    return int(a * x + b * x**2 + c * x**3 + d * x**4 + e)

def measure_light(light_id, sensor_id, brightness):
    light.turn_on(entity_id=light_id, brightness=brightness)
    task.wait_until(state_trigger=sensor_id)
    task.sleep(5)

    return int(float(state.get(sensor_id)))

def gather_lux_levels(light_id, sensor_id):
    from math import ceil

    brightness = [ round(254 / 100 * n) for n in range(0, 105, 5) ]
    lux = [ None for n in range(len(brightness)) ]

    n = 0
    j = ceil(len(brightness) / 2)
    while None in lux:
        log.debug(f"{len([ l for l in lux if l == None])} light levels remaining to test for {light_id}")
        n += j
        i = n % len(brightness)

        lux[i] = measure_light(light_id, sensor_id, brightness[i])

    minimum = measure_light(light_id, sensor_id, 1)
    light.turn_off(entity_id=light_id)

    return [lux, brightness, minimum, lux[-1]]

def get_polynomials(lux, brightness):
    import requests

    data = { 'a': lux, 'b': brightness }
    response = task.executor(requests.post, 'https://ldoicax1a9.execute-api.us-east-1.amazonaws.com/dev/', json=data)
    data = response.json()

    return [data['a'], data['b']]