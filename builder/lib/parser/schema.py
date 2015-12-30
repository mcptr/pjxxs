import argparse

from . import db

parser = argparse.ArgumentParser(
	conflict_handler="resolve",
	add_help=False,
	parents=[db.parser]
)
