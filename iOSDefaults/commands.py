from pymobiledevice3.services.house_arrest import HouseArrestService
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.usbmux import list_devices

from pprint import pprint
import plistlib

def read(device_udid, bundle, key):
	lockdown = create_using_usbmux(serial=device_udid, autopair=True)

	has = HouseArrestService(lockdown=lockdown, bundle_id=bundle)

	i = has.get_file_contents(f'Library/Preferences/{bundle}.plist')
	p = plistlib.loads(i)
	pprint (p[key] if key else p)


def write(device_udid, bundle, key, value, array_add=False, dict_add=False):
	lockdown = create_using_usbmux(serial=device_udid, autopair=True)

	has = HouseArrestService(lockdown=lockdown, bundle_id=bundle)

	i = has.get_file_contents(f'Library/Preferences/{bundle}.plist')
	p = plistlib.loads(i)

	if array_add:
		if key not in p:
			p[key] = []
		p[key].extend(value)
	elif dict_add:
		if key not in p:
			p[key] = {}
		p[key].update(value)
	else:
		p[key] = value

	has.set_file_contents(f'Library/Preferences/{bundle}.plist', plistlib.dumps(p))


def delete(device, bundle, key):
	lockdown = create_using_usbmux(serial=device, autopair=True)

	has = HouseArrestService(lockdown=lockdown, bundle_id=bundle)

	i = has.get_file_contents(f'Library/Preferences/{bundle}.plist')
	p = plistlib.loads(i)

	if key in p:
		del p[key]

	has.set_file_contents(f'Library/Preferences/{bundle}.plist', plistlib.dumps(p))


####


def list():
	devices = list_devices()
	for device in devices:
		lockdown = create_using_usbmux(device.serial, autopair=False, connection_type=device.connection_type)
		print(lockdown.short_info['DeviceName'], f'({device.serial})')