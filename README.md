# HueCastAutoLights
A small program to control hue lights based on the cast status of a chromecast. Essentially this watches the IP address of a given chromecast and if some app is casting to it will turn off a given set of phillips hue lights. Then when the app stops casting to that chromecast the lights will come back on. 

## Dependencies
Dependencies are listed in requirements.txt, additionally this must be run using python 3 (only tested on 3.7 and heigher, though I don't think there is any reason why it should not run on most versions of Python 3)

Note that last point, this is only built for Python 3

## Installation 
  1) clone this repository to somecomputer you want the watch program to run on (ideally this is some computer which will always be on and can have a script running in the background at all times, I am using a rasbperry pi)
  2) Using some python 3 interpriter run autoConfiguration.py and follow its steps.
  2b) If you changed the install path from the defualt install path set an enviromental variable HUE_CAST_DIR to whatever that install path is
  3) Using some Python 3 interpriter run main.py, confirm that you see the rule you added when you ran autoConfigure.py
  4) If you wish to add more rules run autoConfigure again, you will be able to add new rules without reinstalling or registering a new user on the brige
  
## Planned Stuff
  1) More complex rule system -- for when you want your lights behavior to be customizable rule to rule
  2) Better conig file system using xml
  3) Muffins
  
## Other Code Used
Thanks to 
  1) https://github.com/studioimaginaire/phue
  2) https://github.com/rdespoiu/PyPHue/blob/master/LICENSE
  3) https://github.com/balloob/pychromecast
