from .. schema.column import SchemaColumn


class CodegenColumn(SchemaColumn):
	def __init__(self, *args, **kwargs):
		SchemaColumn.__init__(self, *args, **kwargs)
