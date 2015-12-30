import os
from distutils import dir_util

from . manager import Manager


class SchemaManager(Manager):
	def __init__(self, program_args, **kwargs):
		Manager.__init__(self, program_args, **kwargs)
		self._src_dir = self._mk_path(program_args.schema_in)
		self._output_dir = self._mk_path(program_args.schema_out)

	def build(self):
		self.p_info("Running 'build'")

		for (root, dirs, files) in os.walk(self._src_dir):
			if root == self._src_dir:
				continue
			subdir = root.replace(os.path.join(self._src_dir, ""), "")
			dest = os.path.join(self._output_dir, subdir)
			try:
				if not os.path.isdir(dest):
					os.makedirs(dest)
					self.p_info("Created dir: ", dest)
			except OSError as e:
				pass

			for f in files:
				if f.endswith(".py") and f != "__init__.py":
					builder_path = os.path.join(subdir, f)
					outfile = os.path.join(dest, f.replace(".py", ".json"))
					self.p_info("%-32s %s" % (builder_path, outfile))
					builder = os.path.join(root, f)
					st = os.system("python3 '%s' > '%s'" % (builder, outfile))
					if st:
						msg = "Failed to build: %s" % builder
						if self.is_fatal():
							raise Exception(msg)
						else:
							self.p_error(msg)
