import factory      # https://factoryboy.readthedocs.io/en/latest/
import random


class RandomInstance(factory.LazyFunction):

    def __init__(self, model_class, *args, **kwargs):
        choices = range(model_class.objects.count())
        super(RandomInstance, self).__init__(
            function=lambda: model_class.objects.all()[random.choice(choices)],
            *args, **kwargs)