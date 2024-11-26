import sys

import argparse
from .commands import write, read, delete, list

def error(message):
	print(f"Error: {message}", file=sys.stderr)
	sys.exit(1)

def parse_type_value(args):
	"""Parse a value argument into a typed value."""
	type = args.pop(0)
	if type == "-int":
		value = int(args.pop(0))
	elif type == "-float":
		value = float(args.pop(0))
	elif type == "-bool":
		value = args.pop(0).lower() in ["true", "yes", "1"]
	elif type == "-data":
		value = args.pop(0)
	elif type == "-string":
		value = args.pop(0)
	elif type in ("-array", "-array-add", "-dict", "-dict-add"):
		raise ValueError("Nested composite types are not supported")
	else:
		value = type
	return value

def parse_array(array_args):
	"""Parse an array argument into typed elements."""
	parsed_array = []
	while array_args:
		parsed_array.append(parse_type_value(array_args))

	return parsed_array

def parse_dict(dict_args):
	"""Parse a dictionary argument into typed key-value pairs."""
	parsed_dict = {}
	while dict_args:
		key = dict_args.pop(0)
		value = parse_type_value(dict_args)
		parsed_dict[key] = value

	return parsed_dict

def main():
	parser = argparse.ArgumentParser(prog=sys.argv[0])
	parser.add_argument('-d', '--device', type=str, help='UUID of the device', required=False)
	subparsers = parser.add_subparsers(dest='command', help='subcommand help')

	list_devices_parser = subparsers.add_parser('list', help='list all devices')

	read_parser = subparsers.add_parser('read', help='read defaults')
	read_parser.add_argument('bundle', type=str, help='app bundle id to read')
	read_parser.add_argument('key', type=str, help='key to read', nargs='?')

	write_parser = subparsers.add_parser('write', help='write defaults')
	write_parser.add_argument('bundle', type=str, help='app bundle id to write')
	write_parser.add_argument('key', type=str, help='key to write')
	value_group = write_parser.add_mutually_exclusive_group(required=True)
	value_group.add_argument("value", nargs="?", help="The value to write (general string).")
	value_group.add_argument("-string", dest="string_value", help="A string value.")
	value_group.add_argument("-data", dest="data_value", help="Hexadecimal data.")
	value_group.add_argument("-int", "-integer", dest="int_value", type=int, help="An integer value.")
	value_group.add_argument("-float", dest="float_value", type=float, help="A floating-point value.")
	value_group.add_argument("-bool", "-boolean", dest="bool_value", choices=["true", "false", "yes", "no", "1", "0"], help="A boolean value (true, false, yes, no, 1, 0).")
	value_group.add_argument("-array", dest="array_values", nargs=argparse.REMAINDER, help="An array of values with their types (-string, -int, etc.).")
	value_group.add_argument("-array-add", dest="array_add_values", nargs=argparse.REMAINDER, help="An array of values with their types (-string, -int, etc.) to append to existing array.")
	value_group.add_argument("-dict", dest="dict_values", nargs=argparse.REMAINDER, help="An dictionary of key and values with their types (-string, -int, etc.).")
	value_group.add_argument("-dict-add", dest="dict_values", nargs=argparse.REMAINDER, help="An dictionary of key and values with their types (-string, -int, etc.) to add to existing array.")

	delete_parser = subparsers.add_parser('delete', help='delete defaults')
	delete_parser.add_argument('bundle', type=str, help='app bundle id to delete')
	delete_parser.add_argument('key', type=str, help='key to delete')

	args = parser.parse_args()


	if args.command == 'read':
		read(args.device, args.bundle, args.key)

	elif args.command == 'write':
		if args.string_value is not None:
			value = str(args.string_value)
		elif args.data_value is not None:
			value = str(args.data_value)
		elif args.int_value is not None:
			value = int(args.int_value)
		elif args.float_value is not None:
			value = float(args.float_value)
		elif args.bool_value is not None:
			value = args.bool_value.lower() in ["true", "yes", "1"]
		elif args.array_values is not None:
			try:
				value = parse_array(args.array_values)
			except ValueError as e:
				print(f"Error parsing array: {e}")
				return
		elif args.array_add_values is not None:
			try:
				value = parse_array(args.array_add_values)
			except ValueError as e:
				print(f"Error parsing array: {e}")
				return
		elif args.dict_values is not None:
			try:
				value = parse_dict(args.dict_values)
			except ValueError as e:
				print(f"Error parsing array: {e}")
				return
		else:
			value = args.value
			value_type = "default"

		write(
			args.device,
			args.bundle,
			args.key,
			value,
			array_add=args.array_add_values is not None,
			dict_add=args.dict_values is not None
		)
	elif args.command == 'delete':
		delete(args.device, args.bundle, args.key)
	elif args.command == 'list':
		list()
	else:
		parser.print_help()
