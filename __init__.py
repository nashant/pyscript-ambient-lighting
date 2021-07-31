from . import ambilight as ambi
from . import services
from . import utils

def process_config_entry(ambilight):
    ambilight['id'] = f"pyscript.{ambilight['name']}"

    if 'lux_minimum' in ambilight: ambilight['lux_minimum'] = int(ambilight['lux_minimum'])
    if 'lux_maximum' in ambilight: ambilight['lux_maximum'] = int(ambilight['lux_maximum'])

    if 'polynomial_lux' in ambilight:
        if len(ambilight['polynomial_lux']) != 5:
            raise(f"Too few values for polynomial_lux, expecting 5 got {len(ambilight['polynomial_lux'])}")
        ambilight['polynomial_lux'] = [ float(n) for n in ambilight['polynomial_lux'] ]

    if 'polynomial_brightness' in ambilight:
        if len(ambilight['polynomial_brightness']) != 5:
            raise(f"Too few values for polynomial_brightness, expecting 5 got {len(ambilight['polynomial_brightness'])}")
        ambilight['polynomial_brightness'] = [ float(n) for n in ambilight['polynomial_brightness'] ]

    return ambilight

@time_trigger('startup')
def init_ambient_lighting():
    if 'apps' not in pyscript.config or 'ambient_lighting' not in pyscript.config['apps']:
        log.debug('ambient_lighting not in pyscript.config.apps, not loading')
        return

    ambilights = {}

    for entry in pyscript.app_config:
        ambilight = process_config_entry(entry)
        ambilights[ambilight['name']] = ambi.AmbiLight(**ambilight)