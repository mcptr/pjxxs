from pjxxs.fields import *

schema = Schema("permission", 1)
schema.add_field(String("name", nullable=False, required=True))
schema.add_field(Bool("read", default=False))
schema.add_field(Bool("write", default=False))
