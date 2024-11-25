import sys

def error(message):
	print(f"Error: {message}", file=sys.stderr)
	sys.exit(1)