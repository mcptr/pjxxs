import os
import sys
import jinja2


renderer = jinja2.Environment()


def set_up(base_dir):
	global renderer
	template_dir = os.path.join(base_dir, "templates")
	if not os.path.isdir(template_dir):
		template_dir = os.path.join(
			os.path.abspath(os.path.join(base_dir, "..")), "templates"
		)
	loader = jinja2.FileSystemLoader(template_dir)
	renderer = jinja2.Environment(loader=loader)
	_set_pythonpath(base_dir)


def _set_pythonpath(base_dir):
	try:
		from pjxxs import fields
	except ImportError as e:
		sys.path.append(
			os.path.abspath(os.path.join(base_dir, "..", ".."))
		)
		from pjxxs import fields
		# nope? deal with this.
