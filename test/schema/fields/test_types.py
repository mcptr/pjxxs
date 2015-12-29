from nose.tools import assert_equal
from nose.tools import assert_not_equal
from nose.tools import assert_raises

from pjxxs import fields

types = {
	fields.String : (str, ""),
	fields.Object : (dict, {}),
	fields.Array : (list, []),
	fields.Int : (int, 0),
	fields.Double : (float, 0),
	fields.Bool : (bool, False),
	fields.Null : (None, None),
}


def test_ctors():
	name = "name"
	for t in types:
		o = t(name)
		assert_equal(o.get_ident(), name)
		assert_equal(o.get_base_type(), types[t][0])
		assert_equal(o.get_content(), types[t][1])


def test_nullable():
	name = "name"
	for t in types:
		o = t(name, nullable=True)
		assert_equal(o.get_content(), None)
