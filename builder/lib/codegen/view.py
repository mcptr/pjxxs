from lib.pg.view import View
from . table import CodegenTable


class CodegenView(View, CodegenTable):
	def __init__(self, *args, **kwargs):
		View.__init__(self, *args, **kwargs)
		CodegenTable.__init__(self, *args, **kwargs)
