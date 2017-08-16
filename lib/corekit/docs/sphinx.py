import inspect
from django.utils.html import strip_tags
from django.utils.encoding import force_text
from django.db import models, connections
from django.conf import settings


def get_db_type(field):
    for name in settings.DATABASES:
        db_type = field.db_type(connections[name])
        if db_type:
            return db_type


def process_docstring(app, what, name, obj, options, lines):

    if not inspect.isclass(obj) or not issubclass(obj, models.Model):
        return lines

    for field in obj._meta.fields:
        db_type = get_db_type(field)
        if not db_type:
            continue

        # `help_text`
        help_text = strip_tags(force_text(field.help_text))

        # `verbose_name`
        verbose_name = force_text(field.verbose_name).capitalize()

        if help_text:
            lines.append(u':param {0}: {1}({2})     [{3}]'.format(
                field.attname, verbose_name, help_text, db_type))
        else:
            lines.append(u':param {0}: {1}     [{2}]'.format(
                field.attname, verbose_name, db_type))

        # Add the field's type to the docstring
        if isinstance(field, models.ForeignKey):
            to = field.rel.to
            lines.append(
                u':type {0}: {1} to :class:`~{2}.{3}`'.format(
                    field.attname, type(field).__name__,
                    to.__module__, to.__name__))
        else:
            lines.append(
                u':type {0}: {1}'.format(
                    field.attname, type(field).__name__))

    # finally return doc_string
    return lines


def setup(app):
    ''' SETUP '''
    from django.core.wsgi import get_wsgi_application
    get_wsgi_application()

    # Register the docstring processor with sphinx
    app.connect('autodoc-process-docstring', process_docstring)
