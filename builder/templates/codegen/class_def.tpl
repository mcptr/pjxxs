{% extends "codegen/base_table_hxx.tpl" %}

{%macro field_type(col) -%}
{% if col.record.is_nullable == "YES" -%}boost::optional<{{col.cpp_type}}>{% else -%}{{col.cpp_type -}}{% endif %}
{%- endmacro %}

{%- macro field(col) -%}
	{{field_type(col) }} {{col.record.column_name}} = {{col.cpp_type}}();
{%- endmacro -%}

{% block class_def %}
class {{ data.class_name }} : public nix::core::types::Serializable
{
public:
{%- for col in data.columns %}
	{{ field(col) -}}
{% endfor %}

	virtual void from_message(const nix::Message&);
	virtual nix::Message& to_message();
};
{%- endblock class_def -%}
