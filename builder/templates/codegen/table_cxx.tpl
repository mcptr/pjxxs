#include "{{data.table.table_name-}}.hxx"
#include <ctime>
#include <nix/db/types/array.hxx>

namespace mapping {
namespace {{data.table.table_schema}} {

void {{data.class_name-}}::from_message(const nix::Message& msg)
{
{% for col in data.columns %}
   {%- if col.cpp_type == "std::tm" %}
	long long {{col.record.column_name}}_tl = msg.get("{{col.record.column_name}}",  0LL);
	//if({{col.record.column_name}}_tl > 0) {
	std::time_t {{col.record.column_name}}_time({{col.record.column_name}}_tl);
	{{col.record.column_name}} = *std::localtime(&{{col.record.column_name}}_time);
	//}
   {%- else %}
	{{col.record.column_name}} = msg.get("{{col.record.column_name}}",  {{col.cpp_type}}());
   {%- endif %}
{%- endfor %}
}

nix::Message& {{data.class_name-}}::to_message()
{
{% for col in data.columns -%}
	{%- if col.cpp_type == "std::tm" %}
	{%- set value_var = col.record.column_name.strip() +"_value" %}
	{% if col.record.is_nullable == "YES" -%}
	boost::optional<long long> {{value_var}} = (
		{{col.record.column_name-}}.is_initialized()
		? std::mktime(&(*{{-col.record.column_name-}})) : 0);
	{% else %}
	long long {{value_var}} = std::mktime(&{{-col.record.column_name-}});
	{% endif %}
	{%- else -%}
	{%- set value_var = col.record.column_name.strip() %}
	{%- endif %}
	{%- if col.record.is_nullable == "YES" -%}
	{% set setter = "set_optional" %}
	{%- else -%}
	{% set setter = "set" %}
	{%- endif %}
	{{setter}}("{{-col.record.column_name-}}", {{value_var}});
{%- endfor %}

	return *this;
}

} // {{data.table.table_schema}}
} // mapping
