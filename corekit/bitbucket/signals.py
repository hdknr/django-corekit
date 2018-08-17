from django.dispatch import dispatcher
SignalArgs = ['app_key', 'payload', 'user', 'repo' ]


bitbucket_webhook = dispatcher.Signal(providing_args=SignalArgs)