{% load i18n coredocs %}

{% header_label app.verbose_name 1 %}

{% for opt in app|app_model_opts %}

{% header_label opt.verbose_name 2 %}

| 名称                      | ラベル                         　 | データベースタイプ             | 補足                              |  選択肢 |
| ------------------------ | -------------------------------- | --------------------------- | -------------------------------- | ------ |
{% for field in opt.fields %}| {{ field.name }}         | {{ field.verbose_name }}         | {{ field|db_type:connection }}  | {{ field.help_text }}  | {% if field.choices %} <ul>{% for choice in field.choices %}<li>{{ choice.0 }} : {{ choice.1 }}</li> {% endfor %}</ul>{% endif %}|
{% endfor %}

{% endfor %}{# model #}
