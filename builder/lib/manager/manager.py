import os


class Manager(object):
	def __init__(self, args, **kwargs):
		self._args = args

	def _mk_path(self, *args):
		return os.path.join(self._args.workdir, *args)

	def is_verbose(self):
		return (self._args.verbose or self._args.debug)

	def is_debug(self):
		return (self._args.debug)

	def is_fatal(self):
		return (self._args.fatal)

	def p_info(self, *args):
		if self.is_verbose():
			print("#", *args)

	def p_debug(self, *args):
		if self.is_debug():
			print("###", *args)

	def p_error(self, *args):
		print("[ERROR]", *args)

