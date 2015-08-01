__author__ = 'rane'

import os, sys, inspect, thread, time
src_dir = os.path.dirname(inspect.getfile(inspect.currentframe()))
arch_dir = 'lib'
sys.path.insert(0, os.path.abspath(os.path.join(src_dir, arch_dir)))
import Leap
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
import lazylights
import math

MAX_RAW_VALUE = float(65535)
MAX_HUE_VALUE = 360
BRIGHTNESS_MODIFIER = 0.01
HUE_MODIFIER = 5

# the maximum palm y position values for setting brightness
MAX_Y_BRIGHTNESS = 350
MIN_Y_BRIGHTNESS = 50
MIN_Y_BRIGHTNESS_DIFFERENCE = float(MAX_Y_BRIGHTNESS - MIN_Y_BRIGHTNESS)


class BulbState:
    """
        Describes the state of a bulb that will be applied to a lifx bulb using the lazylights api
    """

    is_on = False
    hue = 360       # 0/360 = red
    saturation = 1  # 0 - 1
    brightness = 1  # 0 to 1
    kelvin = 2000   # 2000 warmest, 8000 coolest

    def __init__(self, state):
        # initializes from a lifx bulb state
        self.hue = (state.hue / MAX_RAW_VALUE) * MAX_HUE_VALUE
        self.saturation = state.saturation / MAX_RAW_VALUE
        self.brightness = state.brightness / MAX_RAW_VALUE
        self.kelvin = state.kelvin
        self.is_on = state.power == MAX_RAW_VALUE

    def change_brightness(self, up=True):
        if up and self.brightness < 1:
            self.brightness += BRIGHTNESS_MODIFIER
            self.brightness = 1 if self.brightness > 1 else self.brightness
        elif self.brightness > 0:
            self.brightness -= BRIGHTNESS_MODIFIER
            self.brightness = 0 if self.brightness < 0 else self.brightness

    def change_hue(self, up=True):
        if up:
            self.hue += HUE_MODIFIER
            if self.hue >= MAX_HUE_VALUE:
                self.hue -= MAX_HUE_VALUE
        else:
            self.hue -= HUE_MODIFIER
            if self.hue <=0:
                self.hue += MAX_HUE_VALUE


class BulbCollection:
    """
    Describes the state of a collection of bulbs that needs to be applied to the actual bulbs
    """
    initial_state = None
    current_state = None
    bulbs = None

    def __str__(self):
        return "Hue: %d, Saturation: %f, Brightness: %f, Kelvin: %d, Is On: %s" \
               % (self.hue, self.saturation, self.brightness, self.kelvin, self.is_on)

    def __init__(self):
        self.bulbs = lazylights.find_bulbs()
        states = lazylights.get_state(self.bulbs)
        if states:
            self.initial_state = BulbState(states[0])  # being lazy, we'll just use the first bulb's state
            self.current_state = BulbState(states[0])

    def toggle_power(self):
        """
        Toggles the bulb collection's power on or off
        """
        self.current_state.is_on = not self.current_state.is_on
        lazylights.set_power(self.bulbs, self.current_state.is_on)

    def change_brightness(self, up=True):
        self.current_state.change_brightness(up)
        self.update_bulbs()

    def change_hue(self, up=True):
        self.current_state.change_hue(up)
        self.update_bulbs()

    def set_brightness(self, brightness):
        self.current_state.brightness = brightness
        #self.update_bulbs()

    def set_hue(self, hue):
        self.current_state.hue = hue
        #self.update_bulbs()

    def set_saturation(self, sat):
        self.current_state.saturation = sat

    def update_bulbs(self):
        """
        Updates the bulbs with the state of the collection
        """
        if self.current_state.is_on:
            lazylights.set_state(self.bulbs, self.current_state.hue,
                                 self.current_state.saturation, self.current_state.brightness,
                                 self.current_state.kelvin, 0)


class LightListener(Leap.Listener):
    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
    bulb_collection = None

    def set_bulbs(self, bc):
        self.bulb_collection = bc

    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        # Get hands
        for hand in frame.hands:

            #handType = "Left hand" if hand.is_left else "Right hand"

            #print "  %s, id %d, position: %s, pinch: %d" % (
            #    handType, hand.id, hand.palm_position, hand.pinch_strength)

            palm_x = hand.palm_position[0]
            palm_y = hand.palm_position[1]
            palm_z = hand.palm_position[2]  # trying to unpack results in a ValueError

            if hand.is_left:
                brightness = (palm_y - MIN_Y_BRIGHTNESS) / MIN_Y_BRIGHTNESS_DIFFERENCE
                brightness = 1 if brightness > 1 else brightness
                self.bulb_collection.set_brightness(brightness)

            elif hand.is_right:
                sat = (palm_y - MIN_Y_BRIGHTNESS) / MIN_Y_BRIGHTNESS_DIFFERENCE
                sat = 1 if sat > 1 else sat
                self.bulb_collection.set_saturation(sat)

                rads = math.atan2(palm_x, palm_z)
                deg = rads * float(180 / math.pi) + 180
                print deg
                self.bulb_collection.set_hue(int(deg))

        self.bulb_collection.update_bulbs()

        # Get gestures
        for gesture in frame.gestures():

            if gesture.type == Leap.Gesture.TYPE_SWIPE:
                self.bulb_collection.toggle_power()

def main():
    bc = BulbCollection()
    listener = LightListener()
    listener.set_bulbs(bc)

    controller = Leap.Controller()

    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)

        # reset lights
        bc.current_state = bc.initial_state
        bc.update_bulbs()

if __name__ == "__main__":
    main()