# Handylights

Handylights is a very simple python script that allows you to control your lifx lightbulbs
using a Leap Motion controller.

# Requirements

* Python 2
* One or more Lifx bulbs, updated to the 2.0 firmware
* lazylights - https://github.com/mpapi/lazylights
* a Leap Motion Controller

# Quickstart

You may need to follow the instructions under "Using a Different Python Distribution" on the following page to enable
the LeapPython.so under lib for mac or linux -
https://developer.leapmotion.com/documentation/python/devguide/Project_Setup.html#using-a-different-python-distribution

# Usage

After Running the script, the height of the left hand (more specifically palm) relative to the leap motion controller
controls the brightness, and the height of the right hand controls the color saturation.  The angle of the right hand
relative to the controller sets the color, where the 12 o'clock position is red.

# More

You can buy lifx lightbulbs here: http://mbsy.co/lifx/4464505