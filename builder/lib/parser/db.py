import argparse

from . import generic

parser = argparse.ArgumentParser(
	add_help=False,
	conflict_handler="resolve",
	parents=[generic.parser]
)

parser.add_argument(
	"--host", "-H",
	dest="host",
	default="localhost"
)

parser.add_argument(
	"--port", "-p",
	dest="port",
	type=int,
	default=5432
)

parser.add_argument(
	"--user", "-U",
	dest="user",
	default=""
)

parser.add_argument(
	"--password", "-P",
	dest="password",
	default=""
)

parser.add_argument(
	"--dbname", "-D",
	dest="dbname",
	default=""
)
