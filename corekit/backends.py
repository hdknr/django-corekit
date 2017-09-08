# -*- coding: utf-8 -*-


class PermissionBackend(object):
    def has_perm(self, user_obj, perm, obj=None):
        '''
        :param user_obj: User instance
        :param perm: permission code string (`auth.change_auth_user`)
        :param obj: Model instance (optional)
        '''
        res = obj and hasattr(obj, 'has_perm') and obj.has_perm(user_obj, perm)
        return res or False

    def authenticate(self, username=None, password=None):
        pass
