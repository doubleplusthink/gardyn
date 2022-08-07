#coding=utf-8
import os
import time
import RPi.GPIO as GPIO

from config import CHANNEL_BUTTON, RESET_THRESH, NETWORK_RESET_FILE, NETWORK_SWITCH_SH
from sensors.LED import led

class Button(object):
    """Detect edges on the given GPIO channel."""

    def __init__(self,
                 channel=CHANNEL_BUTTON,
                 polarity=GPIO.FALLING,
                 pull_up_down=GPIO.PUD_UP,
                 debounce_time=0.08):
        """A simple GPIO-based button driver.
        This driver supports a simple GPIO-based button. It works by detecting
        edges on the given GPIO channel. Debouncing is automatic.
        Args:
          channel: the GPIO pin number to use (BCM mode)
          polarity: the GPIO polarity to detect; either GPIO.FALLING or
            GPIO.RISING.
          pull_up_down: whether the port should be pulled up or down; defaults to
            GPIO.PUD_UP.
          debounce_time: the time used in debouncing the button in seconds.
        """

        if polarity not in [GPIO.FALLING, GPIO.RISING]:
            raise ValueError(
                'polarity must be one of: GPIO.FALLING or GPIO.RISING')

        self.channel = int(channel)
        self.polarity = polarity
        self.expected_value = polarity == GPIO.RISING
        self.debounce_time = debounce_time
        
        if not GPIO.getmode():
            GPIO.setmode(GPIO.BCM)     # Numbers GPIOs by GPIO pin, not physical location
        
        GPIO.setup(channel, GPIO.IN, pull_up_down=pull_up_down)

        self.callback = None

    def wait_for_press(self):
        """Waits for the button to be pressed.
        This method blocks until the button is pressed.
        """
        GPIO.add_event_detect(self.channel, self.polarity)
        while True:
            if GPIO.event_detected(self.channel) and self._debounce():
                GPIO.remove_event_detect(self.channel)
                return
            time.sleep(0.02)

    def on_press(self, callback):
        """Calls the callback whenever the button is pressed.
        Args:
          callback: a function to call whenever the button is pressed. It should
            take a single channel number. If the callback is None, the previously
            registered callback, if any, is canceled.
        Example:
          def MyButtonPressHandler(channel):
              print "button pressed: channel = %d" % channel
          my_button.on_press(MyButtonPressHandler)
        """
        GPIO.remove_event_detect(self.channel)
        if callback is not None:
            self.callback = callback
            GPIO.add_event_detect(
                self.channel, self.polarity, callback=self._debounce_and_callback)

    def _debounce_and_callback(self, _):
        long_holding = False
        start_holding = time.time()
        if self._debounce():
            # long holding for reset to NAT mode
            while GPIO.input(self.channel) == self.expected_value:
                if time.time() - start_holding > RESET_THRESH:
                    if long_holding == False:
                        long_holding = True
                        with open(NETWORK_RESET_FILE, 'w') as fp:
                            fp.write('reset')
                        os.system('bash {} NAT'.format(NETWORK_SWITCH_SH))
                        os.system('systemctl start wifi-pairing')
                        led.blink(3)
            if not long_holding:
                self.callback()
 

    def _debounce(self):
        """Debounces the GPIO signal.
        Check that the input holds the expected value for the debounce
        period, to avoid false trigger on short pulses.
        """
        start = time.time()
        while time.time() < start + self.debounce_time:
            if GPIO.input(self.channel) != self.expected_value:
                return False
            time.sleep(0.01)
        return True
                        