{% if conf.ENGINE == 'django.db.backends.mysql' %}
CREATE DATABASE {{ conf.NAME}}
DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
GRANT ALL on {{ conf.NAME }}.*
to '{{ conf.USER }}'@'{{ conf.SOURCE|default:"localhost" }}'
identified by '{{ conf.PASSWORD }}' WITH GRANT OPTION;
{% endif %}
