# coding: utf-8

from django.conf import settings
import os


DOCUMENT_BASE = getattr(
    settings, 'DOCUMENT_BASE', os.path.join(settings.BASE_DIR, 'docs'))

SCHEMASPY = {
    'JAR':  '~/.m2/repository/org/schemaspy/schemaspy/6.0.0-rc1/schemaspy-6.0.0-rc1.jar',   # NOQA
    'JAVA': 'java',
    'PROVIDER': {'mysql': '/usr/share/java/mysql-connector-java.jar', },                    # NOQA Debian
    'DOCBASE': os.path.join(DOCUMENT_BASE, 'source/_static'),
}


def schemaspy_command(database):
    '''
    SchemaSpy
    $ cd
    $ git clone https://github.com/schemaspy/schemaspy.git
    $ cd schemaspy
    $ ./mvnw install

    prerequieste:

    $ sudo apt-get install default-jdk default-jre libmysql-java
    '''
    db = settings.DATABASES[database]
    engine = {'django.db.backends.mysql': 'mysql', }.get(db['ENGINE'], '')

    if not engine:
        return

    params = getattr(settings, 'SCHEMASPY', SCHEMASPY)
    params.update(db)

    params['HOST'] = params.get('HOST', 'localhost')
    params['OUT'] = os.path.join(params['DOCBASE'], params['NAME'])
    params['ENGINE_JAR'] = params['PROVIDER'][engine]
    params['ENGINE_TYPE'] = engine

    command = '{JAVA} -jar {JAR}  -dp {ENGINE_JAR} -t {ENGINE_TYPE} -s {NAME} -host {HOST} -db {NAME} -u {USER} -p {PASSWORD} -o {OUT}'    # NOQA
    return command.format(**params)
