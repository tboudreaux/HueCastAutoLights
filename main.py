import phue as ph
import pychromecast
import time
import os
from pathlib import Path

def get_bridge(ip, USER):
    bridge = ph.Bridge(ip, username=USER)
    return bridge

def setLights(bridge, lights, selfStateList):
    for light, selfState in zip(lights, selfStateList):
        bridge.set_light(light, 'on', selfState)

def connect_to_chromecast(ip):
    TV = pychromecast.Chromecast(ip)
    return TV

def is_cast(chromecast):
    if chromecast.status.display_name == "Backdrop":
        return False
    elif chromecast.status.display_name != "Backdrop" and chromecast.status.display_name != 'Spotify':
        return True

def get_group_state(bridge, lights):
    state = list()

    for light in lights:
        state.append(bridge.get_light(light, 'on'))

    return state

def run_watch(TVs, bridge, rule_lights):
    predictedStates = [None]*len(TVs)
    prevStates = [None]*len(TVs)

    firstCasts = [True]*len(TVs)
    manualOverides = [False]*len(TVs)

    initial_states = list()
    num_rule_lights = list()
    for idx, (TV, lights) in enumerate(zip(TVs, rule_lights)):
        initial_states.append(get_group_state(bridge, lights))
        num_rule_lights.append(len(initial_states[idx]))
    while True:
        for idx, (TV, lights) in enumerate(zip(TVs, rule_lights)):
            if is_cast(TV):
                prevStates[idx] = predictedStates[idx]
                if not manualOverides[idx]:
                    predictedStates[idx] = [False]*num_rule_lights[idx]
                if firstCasts[idx]:
                    initial_states[idx] = get_group_state(bridge, lights)
                    firstCasts[idx]=False
                else:
                    current_state = get_group_state(bridge, lights)
                    if predictedStates[idx] != current_state:
                        manualOverides[idx] = True
                        predictedStates[idx] = current_state
                        initial_states[idx] = predictedStates[idx]
            else:
                if firstCasts[idx]:
                    initial_states[idx] = get_group_state(bridge, lights)
                prevStates[idx] = predictedStates[idx]
                predictedStates[idx] = initial_states[idx]

                firstCasts[idx]=True
                manualOverides[idx] = False

            setLights(bridge, lights, predictedStates[idx])
        time.sleep(1)

def load_chromecast_data(chromecast_file):
    with open(chromecast_file, 'r') as f:
        ip = f.read()
    return ip.rstrip().lstrip()

def load_bridge_data(bridge_file):
    with open(bridge_file, 'r') as f:
        info = f.readlines()
    ip = info[0].rstrip().lstrip()
    user = info[1].rstrip().lstrip()
    return ip, user

def load_light_data(lights_file):
    with open(lights_file, 'r') as f:
        lights = f.readlines()
    lights = [int(x.rstrip().lstrip()) for x in lights]
    return lights

def get_install_dir():
    install_dir = os.environ.get('HUE_CAST_DIR')
    if install_dir is None:
        install_dir = str(Path.home())
        install_dir = install_dir[:-1] if install_dir[-1] == '/' else install_dir
        install_dir = "{}/.HueControl".format(install_dir)
    if not os.path.exists(install_dir):
        raise EnvironmentError("""Install Directory Not Found, either run autoConfig.py or check you set HUE_CAST_DIR enviromental variable correctly""")
    return install_dir

def validate_rules(rule):
    files = os.listdir(rule)
    if 'chromecast_ip' in files and 'light_ids' in files:
        return True
    else:
        return False

def validate_install_dir(install_dir):
    if 'hue_ip_user' in os.listdir(install_dir):
        return True
    else:
        return False

def get_rules():
    install_dir = get_install_dir()
    if validate_install_dir(install_dir):
        rules = next(os.walk(install_dir))[1]
        rules = ["{}/{}".format(install_dir, rule) for rule in rules]
        rules = [x for x in rules if validate_rules(x)]
        print('Running watch, you might want to set this to run in the background [ctrl-c] to close')
        print('Watching for {} rule(s)'.format(len(rules)))

        if len(rules) == 0:
            raise EnvironmentError('No Rules Set, Run autoConfig.py to set a rule and make sure that you have read permissions to the install directory')
        return rules, install_dir
    else:
        print('Unable to locate installation, please run autoConfig')
        exit()

def load_configuration_data():
    rules, install_dir = get_rules()
    chromecast_ips = list()
    lights = list()

    hue_ip_user_file = "{}/hue_ip_user".format(install_dir)
    bridge_ip, bridge_user = load_bridge_data(hue_ip_user_file)

    for rule in rules:
        rule = rule[:-1] if rule[-1] == '/' else rule
        chromecast_ip_file = "{}/chromecast_ip".format(rule)
        lights_id_file = "{}/light_ids".format(rule)

        chromecast_ips.append(load_chromecast_data(chromecast_ip_file))
        lights.append(load_light_data(lights_id_file))
    return chromecast_ips, bridge_ip, bridge_user, lights

if __name__ == '__main__':
    chromecast_ips, bridge_ip, bridge_user, rule_lights = load_configuration_data()

    bridge = get_bridge(bridge_ip, bridge_user)
    TVs = [pychromecast.Chromecast(ip) for ip in chromecast_ips]
    devices = [TV.device for TV in TVs]
    time.sleep(0.5)

    try:
        run_watch(TVs, bridge, rule_lights)
    except KeyboardInterrupt:
        print('\n')
        print('Bye!')

