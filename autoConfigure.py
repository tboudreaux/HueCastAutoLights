import pychromecast
import pyphue
import phue
import time
from pathlib import Path
import os
import shutil

def validate_install_path(install_dir):
    if install_dir:
        if os.path.exists(install_dir):
            return True
        else:
            return False
    else:
        return False

def get_install_location():
    base = str(Path.home())
    base = base[:-1] if base[-1] == '/' else base

    base = "{}/.HueControl".format(base)
    install_dir = None
    while not validate_install_path(install_dir):
        install_dir = input('Enter Install Path or Hit Enter [{}]: '.format(base))
        if install_dir == '':
            install_dir = base
            if not os.path.exists(install_dir):
                os.mkdir(install_dir)
    return install_dir

def get_rule_name(install_dir):
    rule_name = ''
    while rule_name == '':
        rule_name = input('Please Enter Rule Name: ')
    install_dir = install_dir[:-1] if install_dir[-1] == '/' else install_dir

    full_path = "{}/{}".format(install_dir, rule_name.replace(' ', '_'))
    make = True
    if os.path.exists(full_path):
        overwrite = 'h'
        while (overwrite.upper() != '' and overwrite.upper() != 'Y' and overwrite.upper() != 'N'):
            overwrite = input('Would you like to overide the current rule named {} [y/N]: '.format(rule_name))
        if overwrite.upper() == 'Y':
            shutil.rmtree(full_path)
        else:
            exit(1)
    if make:
        os.mkdir(full_path)
    return full_path

def get_chromecasts():
    chromecasts = pychromecast.get_chromecasts()
    name_IP_pair = dict()
    for chromecast in chromecasts:
        name_IP_pair[chromecast.device.friendly_name] = chromecast.host
    return name_IP_pair

def display_cast_names(casts):
    print("Chromecast List:")
    for i, cast in enumerate(casts):
        print("{:<4} {}".format(f"[{i+1}]", cast))

def get_desired_chromecast(casts):
    cast_number = input('Enter the number [1-{}] corresponding to the chromecast you would like to control on: '.format(len(casts)))
    try:
        cast_number = int(cast_number)
    except ValueError:
        return None
    if 1 <= cast_number <= len(casts):
        return cast_number
    else:
        return None

def write_cast_info_file(casts, cast_number, install_loc):
    with open('{}/chromecast_ip'.formar(install_loc), 'w') as f:
        f.write(list(casts.values())[cast_number-1])

def register_new_user_bridge():
    myHue = pyphue.PyPHue(wizard = True)

    return myHue.ip, myHue.user

def write_user_bridge_file(ip, user, install_loc):
    with open('{}/hue_ip_user'.format(install_loc), 'w') as f:
        f.write(ip)
        f.write('\n')
        f.write(user)

def get_lights(ip, user):
    bridge = phue.Bridge(ip, username=user)
    bridge.connect()

    lights = bridge.get_light_objects('name')
    name_id_pair = dict()

    for light in lights:
        name_id_pair[light] = lights[light].light_id

    return name_id_pair

def display_light_names(lights):
    print('Hue Light List:')
    for i, light in enumerate(lights):
        print("{:<4} {}".format(f"[{i+1}]", light))

def parse_light_list(light_list):
    light_list = light_list.split(',')
    light_list = [int(x.lstrip().rstrip()) for x in light_list]
    return light_list

def validate_light_list(lights, light_list):
    okay = True
    for x in light_list:
        if not (1 <= x <= len(lights)):
            okay = False
    return okay

def get_desired_lights(lights):
    light_list = input('Enter the lights you want to control from the list above, seperated by a comma: ')
    try:
        light_list = parse_light_list(light_list)
    except ValueError:
        return None
    if validate_light_list(lights, light_list):
        return light_list
    else:
        return None

def write_light_ids(lights, light_list, install_loc):
    keys = list(lights.values())
    with open('{}/light_ids'.format(install_loc), 'w') as f:
        for light_number in light_list:
            f.write(str(keys[light_number-1]))
            f.write('\n')


if __name__ == '__main__':
    install_dir = get_install_location()
    rule_loc = get_rule_name(install_dir)
    rule_loc = rule_loc[:-1] if rule_loc[-1] == '/' else rule_loc

    # Chromecast Setup
    casts = get_chromecasts()
    display_cast_names(casts)

    cast_number = None
    while not cast_number:
        cast_number = get_desired_chromecast(casts)

    write_cast_info_file(casts, cast_number, rule_loc)

    # Hue User Setup
    ip, user = register_new_user_bridge()
    write_user_bridge_file(ip, user, rule_loc)

    # Hue Lights Setup
    lights = get_lights(ip, user)
    display_light_names(lights)

    light_list = None
    while not light_list:
        light_list = get_desired_lights(lights)
    write_light_ids(lights, light_list, rule_loc)


