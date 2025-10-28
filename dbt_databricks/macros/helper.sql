{% macro helper() %}

    {% set sql_commands = [
        "Add your SQL commands here"
    ]%}

    {% if execute %}

        {% for command in sql_commands %}
            {{ log("executing: " ~ command, info = True) }}
            {% set results = run_query(command) %}
            {% do results.print_table() %}

        {% endfor%}
    
    {% endif %}

{% endmacro %}