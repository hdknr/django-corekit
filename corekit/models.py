def dup_instance(instance, updates={}, exclude=['id', 'pk']):
    '''duplicate instance'''
    params = dict(
        (f.name, getattr(instance, f.name, None))
        for f in instance._meta.fields
        if f.name not in exclude)
    params.update(updates)
    return instance._meta.model.objects.create(**params)