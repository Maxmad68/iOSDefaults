from pymobiledevice3.usbmux import list_devices
import cli

def get_device():
	# Listing all connected devices locally
	usbmux_devices = list_devices()

	if len(usbmux_devices) == 0:
		cli.error("No device connected")
		return None

	return usbmux_devices[0].serial

def verify_device(uuid):
	usbmux_devices = list_devices()

	for device in usbmux_devices:
		if device.serial == uuid:
			return device

	cli.error(f"Device with UDID {uuid} not found")
	return None