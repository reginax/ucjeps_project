This Python package provides a custom Django authentication "back-end" for connecting to a CollectionSpace Services
instance. For more details on how to customize Django's authentication mechanism read the information at the following
link: https://docs.djangoproject.com/en/dev/topics/auth/customizing/

To configure your Django site/project to use this custom authentication "back-end", add the full qualified "CSpaceAuthN"
class name to the "AUTHENTICATION_BACKENDS" variable in your Django site's main .settings file.  For example,

#
# AuthN backends
#
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # the default "Admin" AuthN provider
    'authn.authn.CSpaceAuthN',
)

Before Django can use the "CSpaceAuthN" backend successfully, the "CSpaceAuthN" class needs to be initialized
to connect to a CollectionSpace Services instance. Modify the values under the "[cspace_authn_connect]" section
of the "/cspace_django_project/cspace_django_site/main.cfg" file.
