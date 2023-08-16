
import os
import time
import sys
from pynput import keyboard
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ePuck import ePuck


# You can use this dictionary to asociate an ePuck ID with its MAC Address
epucks = {
    '2971': '10:00:E8:D3:AA:C0',
    '3147': '10:00:E8:AD:78:18',
}


def log(text):
    """	Show @text in standart output with colors """

    blue = '\033[1;34m'
    off = '\033[1;m'

    print((''.join((blue, '[Log] ', off, str(text)))))


def error(text):
    red = '\033[1;31m'
    off = '\033[1;m'

    print((''.join((red, '[Error] ', off, str(text)))))


class Robot(ePuck):

    GLOBAL_SPEED = 180

    def __init__(self, mac_address, debug=False, speed=GLOBAL_SPEED):
        super().__init__(mac_address, debug)
        self.speed = speed

    def forward(self):
        self.set_motors_speed(self.speed, self.speed)

    def backward(self):
        self.set_motors_speed(-self.speed, -self.speed)

    def left(self):
        self.set_motors_speed(-self.speed, self.speed)

    def right(self):
        self.set_motors_speed(self.speed, -self.speed)

    def hold(self):
        self.set_motors_speed(0, 0)

    def forward_right(self):
        self.set_motors_speed(self.speed, int(self.speed/2))

    def forward_left(self):
        self.set_motors_speed(int(self.speed/2), self.speed)

    def backward_right(self):
        self.set_motors_speed(-self.speed, int(-self.speed/2))

    def backward_left(self):
        self.set_motors_speed(int(-self.speed/2), -self.speed)

    def connect(self):
        try:
            super().connect()
            leds_on = [0] * 8
            log('Connection complete. CTRL+C to stop')
            log('Library version: ' + self.version)
            times_got = []

        except Exception as e:
            error(e)
            sys.exit()

    def controller(self, key):
        if key == 'w':
            self.forward()
        elif key == 's':
            self.backward()
        elif key == 'a':
            self.left()
        elif key == 'd':
            self.right()
        elif key == 'wa':
            self.forward_left()
        elif key == 'wd':
            self.forward_right()
        elif key == 'sa':
            self.backward_left()
        elif key == 'sd':
            self.backward_right()
        elif key == 'space':
            self.hold()


if __name__ == '__main__':
    # X = '([a-fA-F0-9]{2}[:|\-]?){6}'
    # if len(sys.argv) < 2:
    #     error("Usage: " + sys.argv[0] + " ePuck_ID | MAC Address")
    #     sys.exit()
    # robot_id = sys.argv[1]

    def on_press(key, robot):

        if key == keyboard.Key.esc:
            # Stop listener
            return False

        try:
            key_char = key.char
        except AttributeError:
            key_char = key.name

        robot.controller(key_char)


    def on_activate_wa(robot):
        robot.controller('wa')

    def on_activate_wd(robot):
        robot.controller('wd')

    def on_activate_sa(robot):
        robot.controller('sa')

    def on_activate_sd(robot):
        robot.controller('sd')

    def hot_key_stop():
        return False

    robot_id = '3147'
    mac = 0
    try:
        mac = epucks[robot_id]
    except KeyError:
        error('You have to indicate the MAC direction of the robot')

    robot_1 = Robot(mac, debug=True)
    robot_1.connect()

    listener = (
        keyboard.Listener(on_press=lambda event: on_press(event, robot_1),
                          suppress=True))

    hotkey = keyboard.GlobalHotKeys({
        'w+a': lambda: on_activate_wa(robot_1),
        'w+d': lambda: on_activate_wd(robot_1),
        's+a': lambda: on_activate_sa(robot_1),
        's+d': lambda: on_activate_sd(robot_1),
        '<esc>+q': lambda: hot_key_stop()
    })

    listener.start()
    hotkey.start()

    while True:
        robot_1.step()
        time.sleep(0.5)
        if not listener.running:
            break

    listener.join()

    robot_1.hold()
    robot_1.step()

    robot_1.close()
    sys.exit()
