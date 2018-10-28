import phue as ph
import pychromecast
import time
import os

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

def run_watch(TV, bridge, lights):
    selfState = None
    prevState = None

    firstCast = True
    manualOveride = False

    initial_state = get_group_state(bridge, lights)
    num_lights = len(initial_state)
    while True:
        if is_cast(TV):
            prevState = selfState
            if not manualOveride:
                selfState = [False]*num_lights
            if firstCast:
                initial_state = get_group_state(bridge, lights)
                firstCast=False
            else:
                current_state = get_group_state(bridge, lights)
                if selfState != current_state:
                    manualOveride = True
                    selfState = current_state
                    initial_state = selfState
        else:
            if firstCast:
                initial_state = get_group_state(bridge, lights)
            prevState = selfState
            selfState = initial_state

            firstCast=True
            manualOveride = False

        setLights(bridge, lights, selfState)
        stateChange=False
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

# TODO: Load configuration files from install dir, not from path
def load_configuration_data():
    path = os.environ.get('CAST_HUE_DIR')
    if path is None:
        raise EnvironmentError('Enviromental Variable CAST_HUE_DIR not set')
    else:
        path = path[:-1] if path[-1] == '/' else path
        chromecast_ip_file = "{}/chromecast_ip".format(path)
        hue_ip_user_file = "{}/hue_ip_user".format(path)
        lights_id_file = "{}/light_ids".format(path)

        chromecast_ip = load_chromecast_data(chromecast_ip_file)
        bridge_ip, bridge_user = load_bridge_data(hue_ip_user_file)
        lights = load_light_data(lights_id_file)
    return chromecast_ip, bridge_ip, bridge_user, lights

if __name__ == '__main__':
    chromecast_ip, bridge_ip, bridge_user, lights = load_configuration_data()

    bridge = get_bridge(bridge_ip, bridge_user)
    TV = pychromecast.Chromecast(chromecast_ip)
    device = TV.device
    time.sleep(0.5)

    try:
        run_watch(TV, bridge, lights)
    except KeyboardInterrupt:
        print('\n')
        print('Bye!')

