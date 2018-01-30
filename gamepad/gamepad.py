# -*- coding: utf-8 -*-

import os, struct, array
import time
from fcntl import ioctl
import select

class gamepad():
    
    device_path = "/dev/input"
    device_file = ""
    device_name = ""
    devices_available = []
    timeout = .1
    stop_on_button = False
    do_listen = False

    axes_available = []
    buttons_available = []
    
    # These constants were borrowed from linux/input.h
    axis_names = {
        0x00 : 'x',
        0x01 : 'y',
        0x02 : 'z',
        0x03 : 'rx',
        0x04 : 'ry',
        0x05 : 'rz',
        0x06 : 'throttle',
        0x07 : 'rudder',
        0x08 : 'wheel',
        0x09 : 'gas',
        0x0a : 'brake',
        0x10 : 'hat0x',
        0x11 : 'hat0y',
        0x12 : 'hat1x',
        0x13 : 'hat1y',
        0x14 : 'hat2x',
        0x15 : 'hat2y',
        0x16 : 'hat3x',
        0x17 : 'hat3y',
        0x18 : 'pressure',
        0x19 : 'distance',
        0x1a : 'tilt_x',
        0x1b : 'tilt_y',
        0x1c : 'tool_width',
        0x20 : 'volume',
        0x28 : 'misc',
    }
    
    button_names = {
        0x120 : 'trigger',
        0x121 : 'thumb',
        0x122 : 'thumb2',
        0x123 : 'top',
        0x124 : 'top2',
        0x125 : 'pinkie',
        0x126 : 'base',
        0x127 : 'base2',
        0x128 : 'base3',
        0x129 : 'base4',
        0x12a : 'base5',
        0x12b : 'base6',
        0x12f : 'dead',
        0x130 : 'a',
        0x131 : 'b',
        0x132 : 'c',
        0x133 : 'x',
        0x134 : 'y',
        0x135 : 'z',
        0x136 : 'tl',
        0x137 : 'tr',
        0x138 : 'tl2',
        0x139 : 'tr2',
        0x13a : 'select',
        0x13b : 'start',
        0x13c : 'mode',
        0x13d : 'thumbl',
        0x13e : 'thumbr',
    
        0x220 : 'dpad_up',
        0x221 : 'dpad_down',
        0x222 : 'dpad_left',
        0x223 : 'dpad_right',
    
        # XBox 360 controller uses these codes.
        0x2c0 : 'dpad_left',
        0x2c1 : 'dpad_right',
        0x2c2 : 'dpad_up',
        0x2c3 : 'dpad_down',
    }
    
    
    def __init__(self, device=None, timeout=.1, stop_on_button=False):
        """Instantiates a gamepad instance to interact with gamepads
            
            Use the listen function to get data
            
            Parameters
            ----------
            device : str
                Which device to use. [default = 'js0']
            timeout : float
                How much time to wait for data when there is no activity, in s [default = .1]
            stop_on_button : bool
                To improve performance, the listen function waits until the buffer is empty and 
                returns the most recent data. If a button press is during axis change, it may not   
                register because the buffer won't be empty. Set stop_on_button to True to break   
                out of the listen look on any button press to address this. [default = False]

        """

        devs_in = os.listdir(self.device_path)
        for dev in devs_in:
            if dev.startswith('js'):
                self.devices_available.append(dev)
        
        # Device parameter is intended to allow disambiguation when there 
        # is more than one device, not a full featured way to specify an 
        # arbitrary file path
        if device: 
            for dev in self.devices_available:
                if device == dev:
                    self.device_file = dev
                    break
                elif device == os.path.join(self.device_path, dev):
                    self.device_file = dev
                    
            
        if not self.device_file:
            if len(self.devices_available) > 0:
                self.devices_available.sort()
                self.device_file = self.devices_available[0]
            else:
                raise Exception("No gamepad devices found")

        self.stop_on_button = stop_on_button

        self.device_handle = open(os.path.join(self.device_path, self.device_file), 'rb')
        
        # Get the device name.
        #buf = bytearray(63)
        buf = array.array('c', ['\0'] * 64)
        ioctl(self.device_handle, 0x80006a13 + (0x10000 * len(buf)), buf) # JSIOCGNAME(len)
        self.device_name = buf.tostring().strip("\x00")
#        print('Device name: %s' % js_name)
        
        # Get number of axes and buttons.
        buf = array.array('B', [0])
        ioctl(self.device_handle, 0x80016a11, buf) # JSIOCGAXES
        self.num_axes = buf[0]
        
        buf = array.array('B', [0])
        ioctl(self.device_handle, 0x80016a12, buf) # JSIOCGBUTTONS
        self.num_buttons = buf[0]
        
        # Get the axis map.
        buf = array.array('B', [0] * 0x40)
        ioctl(self.device_handle, 0x80406a32, buf) # JSIOCGAXMAP
        
        for axis in buf[:self.num_axes]:
            axis_name = self.axis_names.get(axis, 'unknown(0x%02x)' % axis)
            self.axes_available.append(axis_name)
#            self.axis_states[axis_name] = 0.0
        
        # Get the button map.
        buf = array.array('H', [0] * 200)
        ioctl(self.device_handle, 0x80406a34, buf) # JSIOCGBTNMAP
        
        for btn in buf[:self.num_buttons]:
            btn_name = self.button_names.get(btn, 'unknown(0x%03x)' % btn)
            self.buttons_available.append(btn_name)
#            self.button_states[btn_name] = 0
        
        initial_values = True
        while initial_values:
            r, w, e = select.select([ self.device_handle ], [], [], 0)
            if self.device_handle in r:
                evbuf = self.device_handle.read(8)
                if evbuf:
                    evtime, evvalue, evtype, evnumber = struct.unpack('IhBB', evbuf)
            
                    if not evtype & 0x80:
                        initial_values = False
            else:
                initial_values = False


    def flush(self):
        buffer_full = True
        while buffer_full:
            d,v = self.listen()
            if not d:
                buffer_full = False


    def listen(self):
        """Listen for gamepad input

        Waits at most timeout s.

        Returns
        -------
        ret : tuple
            A tuple, in which the first element is the device name (axis or button; listed 
            in axes_available and buttons_available), and the second is the state (for axes, 
            a float -1 < 1; for buttons 1 for down, 0 for up)

            To determine which axes and buttons are which for a gamepad, try something like:

            while 1:
                print gamepad.listen()
        """
        ret = (None,None)
        self.do_listen = True
        timeout_start = time.time()
        while self.do_listen:
            r, w, e = select.select([ self.device_handle ], [], [], 0)
            if self.device_handle in r:
                evbuf = self.device_handle.read(8)
                if evbuf:
                    evtime, evvalue, evtype, evnumber = struct.unpack('IhBB', evbuf)
            
                    if evtype & 0x80:
                        # Skip initial states
                         pass
            
                    elif evtype & 0x01:
                        button = self.buttons_available[evnumber]
                        if button:
                            if evvalue:
                                ret = button,0
                                if self.stop_on_button:
                                    # Button presses may be more important than axis changes
                                    # And if a button press is during movement, it may not register
                                    # Because the buffer isn't empty. Set stop_on_button to True 
                                    # to address this.
                                    self.do_listen = False
                            else:
                                ret = button,1
            
                    elif evtype & 0x02:
                        axis = self.axes_available[evnumber]
                        if axis:
                            fvalue = evvalue / 32767.0
                            ret = axis, fvalue
            else:
                # There are two states that break the loop
                # (1) We have data, but most recent poll is empty
                #     That is, if we have data but there is still more, keep polling
                #     Otherwise, performance is sluggish
                # (2) Timeout
                if ret[0] or (time.time() - timeout_start < self.timeout): 
                    self.do_listen = False
                else:
                    # No prev data, no current data, no timeout. Just keep polling
                    pass

        return ret
