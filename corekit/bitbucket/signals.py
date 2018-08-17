from django.dispatch import dispatcher
SignalArgs = ['payload', 'user', 'repo' ]


bitbucket_webhook = dispatcher.Signal(providing_args=SignalArgs)