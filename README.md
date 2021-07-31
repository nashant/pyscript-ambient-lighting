# PyScript Ambient Lighting for Home Assistant

This is a pyscript app for automated ambient lighting control

## Installation

In your `{home assistant config}/pyscript/apps` folder...

`git clone https://github.com/nashant/pyscript-ambient-lighting.git ambient_lighting`

or download the zip and unpack it to `ambient_lighting`

## Configuration

The configuration params are as follows:
| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | yes | The entity id gets set as `pyscript.{name}_ambilight` |
| `friendly_name` | string | yes | This'll be what you see in a dashboard |
| `light_id` | string | yes | The entity id for the light (or group) you want to control |
| `lux_sensor_id` | string | yes | The entity id for the lux sensor you want to take readings from |
| `lux_target_id` | string | yes | The entity id for the lux target, likely an input_number |
| `motion_sensor_id` | string | yes | The entity id for the motion sensor you want to use to control the lights |
| `lux_minimum` | int | no | The lux measured at a brightness value of 1 |
| `lux_maximum` | int | no | The lux measured at a brightness value of 254 |
| `polynomial_lux` | List[float] | no | The calculated values which plug in to the polynomial function to convert lux to brightness |
| `polynomial_brightness` | List[float] | no | The calculated values which plug in to the polynomial function to convert brightness to lux |

The non-required params above are calculated. It is recommended that once they are, you check the state in the developer tools and add them to the yaml config.

Example initial set up:

    pyscript:
      apps:
        ambient_lighting:
        - name: office_ambilight
          friendly_name: Office Ambilight
          light_id: light.office
          lux_sensor_id: sensor.office_lux
          motion_sensor_id: binary_sensor.office_motion

This will create you a `pyscript.office_ambilight` entity. The next step is to calculate the polynomials and measure the lux min/max.

Go to developer tools -> services. Look for `Update Ambilight polynomials` and select the entity you wish to run the calculations for. It's highly recommended that you shut out all other light sources for the room while you're doing this, it would pollute the results if the light you're measuring is not the only light source.

Once it's finished you'll get a persistent notification. Next go to developer tools -> states, find the pyscript entity you just measured, copy the polynomials and lux min/max to your yaml config. It should now look like this:

    pyscript:
      apps:
        ambient_lighting:
        - name: office_ambilight
          friendly_name: Office Ambilight
          light_id: light.office
          lux_sensor_id: sensor.office_lux
          motion_sensor_id: binary_sensor.office_motion
          lux_minimum: 2
          lux_maximum: 28
          polynomial_lux:
          - 22.553399787515726
          - -0.5070252614483315
          - -0.0038974460200340566
          - 0.00022330096277467515
          - -31.54604815309426
          polynomial_brightness:
          - 0.03510989397468139
          - 0.00027997267176783105
          - -0.0000019179037291153174
          - 7.371328420841643e-9
          - 1.7369486752057455

## How it works

21 light measurements will be made then the resulting figures will be processed by a SciPy curve_fit function. Out of that will come 5 numbers which correspond to the function `(a * x) + (b * x^2) + (c * x^3) + (d * x^4) + e`.
I'm running this as an AWS Lambda function, no data apart from the brightness/lux measurements is sent to it.

## Copyright

Copyright (c) 2020-2021 Craig Barratt.  May be freely used and copied according to the terms of the
[Apache 2.0 License](LICENSE).
