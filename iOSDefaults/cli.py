import sys
import argparse
import datetime
import plistlib
from pprint import pprint

class CLI_Error(Exception):
	def __init__(self, message):
		print ("Error: ", message, file=sys.stderr)
		sys.exit(1)

class iOS_Defaults_CLI:
	@staticmethod
	def write(device_udid, bundle, key, value, adding=False):
		from pymobiledevice3.services.house_arrest import HouseArrestService
		from pymobiledevice3.lockdown import create_using_usbmux

		lockdown = create_using_usbmux(serial=device_udid, autopair=True)

		has = HouseArrestService(lockdown=lockdown, bundle_id=bundle)

		i = has.get_file_contents(f'Library/Preferences/{bundle}.plist')
		p = plistlib.loads(i)
		if isinstance(value, list) and adding:
			if key not in p:
				p[key] = []
			p[key].extend(value)
		elif isinstance(value, dict) and adding:
			if key not in p:
				p[key] = {}
			p[key].update(value)
		else:
			p[key] = value

		has.set_file_contents(f'Library/Preferences/{bundle}.plist', plistlib.dumps(p))

	@staticmethod
	def read(device_udid, bundle, key, json_output):
		if json_output:
			import json
			def out(i):
				print (json.dumps(i))
		else:
			out = pprint

		from pymobiledevice3.services.house_arrest import HouseArrestService
		from pymobiledevice3.lockdown import create_using_usbmux

		lockdown = create_using_usbmux(serial=device_udid, autopair=True)

		has = HouseArrestService(lockdown=lockdown, bundle_id=bundle)

		i = has.get_file_contents(f'Library/Preferences/{bundle}.plist')
		p = plistlib.loads(i)
		if key:
			if key not in p:
				raise CLI_Error(f'Key {key} not found in {bundle}.plist')
			out (p[key])
		else:
			out (p)

	@staticmethod
	def delete(device, bundle, key):
		from pymobiledevice3.services.house_arrest import HouseArrestService
		from pymobiledevice3.lockdown import create_using_usbmux

		lockdown = create_using_usbmux(serial=device, autopair=True)

		has = HouseArrestService(lockdown=lockdown, bundle_id=bundle)

		i = has.get_file_contents(f'Library/Preferences/{bundle}.plist')
		p = plistlib.loads(i)

		if key in p:
			del p[key]
		else:
			sys.exit(1)

		has.set_file_contents(f'Library/Preferences/{bundle}.plist', plistlib.dumps(p))

	@staticmethod
	def export_defaults(device, bundle, output):
		from pymobiledevice3.services.house_arrest import HouseArrestService
		from pymobiledevice3.lockdown import create_using_usbmux

		lockdown = create_using_usbmux(serial=device, autopair=True)

		has = HouseArrestService(lockdown=lockdown, bundle_id=bundle)

		i = has.get_file_contents(f'Library/Preferences/{bundle}.plist')
		if output:
			with open(output, 'wb') as f:
				f.write(i)
		else:
			sys.stdout.buffer.write(i)

	@staticmethod
	def import_defaults(device, bundle, input):
		from pymobiledevice3.services.house_arrest import HouseArrestService
		from pymobiledevice3.lockdown import create_using_usbmux

		lockdown = create_using_usbmux(serial=device, autopair=True)

		has = HouseArrestService(lockdown=lockdown, bundle_id=bundle)

		if input:
			with open(input, 'rb') as f:
				i = f.read()
		else:
			i = sys.stdin.buffer.read()

		has.set_file_contents(f'Library/Preferences/{bundle}.plist', i)

	@staticmethod
	def list_devices():
		from pymobiledevice3.lockdown import create_using_usbmux
		from pymobiledevice3.usbmux import list_devices

		devices = list_devices()
		for device in devices:
			lockdown = create_using_usbmux(device.serial, autopair=False, connection_type=device.connection_type)
			print(lockdown.short_info['DeviceName'], f'({device.serial})')


def parse_value(args, in_composite=False):
	"""Parse a single value recursively."""
	if not args:
		raise ValueError("Expected a value but found none.")

	type_token = args.pop(0)
	if type_token == "-string":
		return str(args.pop(0))
	elif type_token == "-data":
		if not args or not all(c in "0123456789abcdefABCDEF" for c in args[0]):
			raise CLI_Error("Expected hex digits after -data")

		return bytes.fromhex(args.pop(0))
	elif type_token in ("-int", "-integer"):
		return int(args.pop(0))
	elif type_token == "-float":
		return float(args.pop(0))
	elif type_token in ("-bool", "-boolean"):
		return args.pop(0).lower() in ["true", "yes", "1"]
	elif type_token == "-date":
		return datetime.fromisoformat(args.pop(0))
	elif type_token in ("-array", "-array-add"):
		if in_composite:
			raise CLI_Error("Nested composite types are not supported.")
		array = []
		while args:
			array.append(parse_value(args, in_composite=True))
		return array
	elif type_token in ("-dict", "-dict-add"):
		if in_composite:
			raise CLI_Error("Nested composite types are not supported.")
		dictionary = {}
		while args:
			key = args.pop(0)
			value = parse_value(args, in_composite=True)
			dictionary[key] = value
		return dictionary

	elif type_token.startswith("-"):
		raise CLI_Error(f"Unknown value type: {type_token}")
	else:
		return type_token

def main():
	parser = argparse.ArgumentParser(prog=sys.argv[0])
	parser.add_argument('-d', '--device', type=str, help='UUID of the device', required=False)
	subparsers = parser.add_subparsers(dest='command', help='subcommand help')

	list_devices_parser = subparsers.add_parser('list-devices', help='list all connected devices\n\r')

	read_parser = subparsers.add_parser('read', help='read defaults')
	read_parser.add_argument('bundle', type=str, help='app bundle id to read')
	read_parser.add_argument('key', type=str, help='key to read', nargs='?')
	read_parser.add_argument('-j', '--json', action='store_true', help='Outputs as JSON', required=False)

	write_parser = subparsers.add_parser('write', help='write key for value')
	write_parser.add_argument('bundle', type=str, help='app bundle id to write')
	write_parser.add_argument('key', type=str, help='key to write')
	write_parser.add_argument(
		"value",
		nargs=argparse.REMAINDER,
		help=(
			"Value to write. Supported formats:\n"
			"  -string <string_value>\n"
			"  -data <hex_digits>\n"
			"  -int[eger] <integer_value>\n"
			"  -float <floating_point_value>\n"
			"  -bool[ean] (true | false | yes | no)\n"
			"  -date <date_representation>\n"
			"  -array <value1> <value2> ...\n"
			"  -dict <key1> <value1> <key2> <value2> ..."
		),
	)

	delete_parser = subparsers.add_parser('delete', help='delete defaults key-value pair')
	delete_parser.add_argument('bundle', type=str, help='app bundle id to delete')
	delete_parser.add_argument('key', type=str, help='key to delete')

	export_parser = subparsers.add_parser('export', help='export all defaults for bundle to stdout or file')
	export_parser.add_argument('bundle', type=str, help='app bundle id to export')
	export_parser.add_argument('--output', '-o', type=str, help='file to export to')

	import_parser = subparsers.add_parser('import', help='import all defaults for bundle')
	import_parser.add_argument('bundle', type=str, help='app bundle id to import')
	import_parser.add_argument('--input', '-i', type=str, help='file to import')

	args = parser.parse_args()


	if args.command == 'read':
		iOS_Defaults_CLI.read(args.device, args.bundle, args.key, args.json)

	elif args.command == 'write':
		adding = args.value and args.value[0] in ("-array-add", "-dict-add")
		value = parse_value(args.value)
		if args.value:
			raise CLI_Error(f"Unexpected arguments: {', '.join(args.value)}")

		iOS_Defaults_CLI.write(
			args.device,
			args.bundle,
			args.key,
			value,
			adding=adding,
		)

	elif args.command == 'delete':
		iOS_Defaults_CLI.delete(args.device, args.bundle, args.key)

	elif args.command == 'list-devices':
		iOS_Defaults_CLI.list_devices()

	elif args.command == 'export':
		iOS_Defaults_CLI.export_defaults(args.device, args.bundle, args.output)

	elif args.command == 'import':
		iOS_Defaults_CLI.import_defaults(args.device, args.bundle, args.input)

	else:
		parser.print_help()

if __name__ == '__main__':
	main()