cspace-django-project
====================

This is a simple example Django-based webapp that can be configured to connect to an instance of the CollectionSpace services.

This is essentially an archetype for creating Django projects (websites) that are setup to run CollectionSpace related webapp applications.  It comes configured with two example webapps. The first is named "polls" that derives from the Django tutorial at https://docs.djangoproject.com/en/dev/intro/tutorial01/.  The second example is named "intakes."

It also comes configured with a "back-end" CollectionSpace authentication provider.  See the README.txt file in the /cspace_django_site/authn directory for instructions on setting it up.

====================

7.23.2013

Public search is in partially 'working' order by hitting the CollectionSpace REST API. Work still needs to be done on the detail view for each object, and on moving to using Solr instead of the REST API for retrieving data. The UI will likely shift, as well, as we better understand the requirements for the public portal. 