import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    ''' Der nachfolgende Key wird konfiguriert, um diesen als kryptographischen Key verwenden zu können, welches von
        wtforms verwendet wird, um Formulare sicherer zu gestalten und diese vor Cross-Site Request Forgery (CSRF)
        zu schützen. '''
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    ''' Im nachfolgenden Ausdruck wird der Ort der Datenbank der Applikation geholt, in der diese sich befindet. Wird
        keine Datenbank gefunden (und ist somit auch keine vorhanden), dann wird eine Datenbank mit dem Namen "app.db" 
        erstellt. Dieses erstellen einer neuen Datenbank erfolgt im "or" Teil des Ausdrucks. '''
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    ''' Als nächstes wird verhindert, dass die Modifikationen getrackt werden, also, dass bei jeder Änderung der 
        Datenbank die Applikation informiert wird '''
    SQLALCHEMY_TRACK_MODIFICATIONS = False
