{% extends "codegen/class_def.tpl" %}
{% block type_conversion_def -%}
using mapping::{{-data.table.table_schema-}}::{{- data.class_name -}};

template<>
struct type_conversion<{{- data.class_name -}}>
{
	typedef values base_type;

	static
	void from_base(values const& v, indicator /* ind */, {{data.class_name -}}& r)
	{
		{% for col in data.columns -%}
		r.{{-col.record.column_name}} = v.get<{{- field_type(col) -}}>("{{-col.record.column_name-}}");
		{% endfor %}
	}

	static
	void to_base(const {{ data.class_name -}}& r, soci::values& v, soci::indicator& ind)
	{
		{%if "view" in [ data.reltype.lower(), data.table.table_schema.lower() ] %}
		throw std::runtime_error("{{ data.class_name -}} is read-only");
		{% else %}
		using namespace nix::util::types;

		{% for col in data.columns -%}
		  {%- if col.record.is_nullable == "YES" -%}
		set_optional_value(v, "{{col.record.column_name}}", r.{{-col.record.column_name-}});
		  {%- else -%}
		v.set("{{-col.record.column_name}}", r.{{-col.record.column_name-}});
		  {%- endif %}
		{% endfor %}
		ind = i_ok;
		{% endif %}
	}
}; // type_conversion<{{- data.class_name -}}>
{%- endblock -%}
