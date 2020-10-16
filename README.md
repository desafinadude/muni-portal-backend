[![codecov](https://codecov.io/gh/OpenUpSA/muni_portal/branch/master/graph/badge.svg)](https://codecov.io/gh/OpenUpSA/muni-portal-backend/)
[![Build Status](https://travis-ci.org/OpenUpSA/muni_portal.png)](https://travis-ci.org/OpenUpSA/muni-portal-backend)


Muni Portal
===========


Project Layout
--------------


### Django

Apps go in the project directory `muni_portal`


### Python

Dependencies are managed via Pipfile in the docker container.

Add and lock dependencies in a temporary container:

    docker-compose run --rm web pipenv install pkgname==1.2.3

Rebuild the image to contain the new dependencies:

    docker-compose build web

Make sure to commit updates to Pipfile and Pipfile.lock to git


### Javascript and CSS

JS and CSS are bundled using [parcel](https://parceljs.org/) - see `package.json`.

Dependencies are managed via `yarn`, e.g.

    docker-compose run --rm web yarn add bootstrap@4.x

Make sure to commit updates to package.json and yarn.lock to git.


Development setup
-----------------

Requires the environment variables `USER_ID=$(id -u)` and `GROUP_ID=$(id -g)` so that the container shares your UID and GID.

In one shell, run the frontend asset builder

    docker-compose run --rm web yarn dev

In another shell, initialise and run the django app

    docker-compose run --rm web bin/wait-for-postgres.sh
    docker-compose run --rm web python manage.py migrate
    docker-compose run --rm web python manage.py loaddata seeddata.json demodata.json
    docker-compose up

If you need to destroy and recreate your dev setup, e.g. if you've messed up your
database data or want to switch to a branch with an incompatible database schema,
you can destroy all volumes and recreate them by running the following, and running
the above again:

    docker-compose down --volumes


### Maintaining the demo data fixture

The demo data fixture was produced using the command

    docker-compose run --rm web python manage.py dumpdata --natural-foreign --indent 2\
      -e contenttypes \
      -e auth.permission \
      -e auth.user \
      -e wagtailcore.groupcollectionpermission \
      -e wagtailcore.grouppagepermission \
      -e wagtailimages.rendition \
      -e sessions \
      -e core.contactdetailtype \
      > demodata.json

Only the minimal data needed to have a working system to click around in and
demonstrate all the features should be included. Avoid including massive amounts
of superfluous data. Update the command above as needed to get as close as possible
to exporting just the necessary data to get a running system.


Running tests
-------------

    docker-compose run --rm web python manage.py test

Tests might fail to connect to the databse if the docker-compose `db` service wasn't running and configured yet. Just check the logs for the `db` service and run the tests again.


Settings
--------

Undefined settings result in exceptions at startup to let you know they are not configured properly. It's one this way so that the defaults don't accidentally let bad things happen like forgetting analytics or connecting to the prod DB in development.


| Key | Default | Type | Description |
|-----|---------|------|-------------|
| `DATABASE_URL` | undefined | String | `postgresql://user:password@hostname/dbname` style URL |
| `DJANGO_DEBUG_TOOLBAR` | False | Boolean | Set to `True` to enable the Django Debug toolbar NOT ON A PUBLIC SERVER! |
| `DJANGO_SECRET_KEY` | undefined | String | Set this to something secret and unguessable in production. The security of your cookies and other crypto stuff in django depends on it. |
| `TAG_MANAGER_CONTAINER_ID` | undefined | String | [Google Tag Manager](tagmanager.google.com) Container ID. [Use this to set up Google Analytics.](https://support.google.com/tagmanager/answer/6107124?hl=en). Requried unless `TAG_MANAGER_ENABLED` is set to `False` |
| `TAG_MANAGER_ENABLED` | `True` | Boolean | Use this to disable the Tag Manager snippets, e.g. in dev or sandbox. |