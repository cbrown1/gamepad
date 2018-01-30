[![Build Status](https://travis-ci.org/cbrown1/gamepad.svg?branch=master)](https://travis-ci.org/cbrown1/gamepad)

# gamepad

A python module to access gamepads from linux machines. 

## Installing

### Download:

```bash
git clone https://github.com/cbrown1/gamepad.git
```

### Compile and install:

```bash
python setup.py build
sudo python setup.py install
```

## Usage
```python
# instantiate gamepad class:
gp = gamepad.gamepad()
# find out which axes and buttons are which:
while 1:
    print gp.listen()
```

## Authors

- **Christopher Brown**

## License

This project is licensed under the GPLv3 - see the [LICENSE.md](LICENSE.md) file for details.
