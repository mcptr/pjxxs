import argparse


parser = argparse.ArgumentParser(
	add_help=False,
	conflict_handler="resolve",
)

parser.add_argument(
	"--verbose", "-v",
	dest="verbose",
	action="store_true",
	default=False
)

parser.add_argument(
	"--debug",
	dest="debug",
	action="store_true",
	default=False,
	help="Enable debug mode"
)

parser.add_argument(
	"--fatal", "-F",
	dest="fatal",
	action="store_true",
	default=False,
	help="Treat all errors as fatal"
)
