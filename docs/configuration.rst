Deployment Configuration
========================

The whole deploy process is configured through a file named ``deploy.conf`` in
your project root. This is a YAML_ file that describes your environment, hosts
that are involved, and how tasks are run on these hosts.

Environments
------------
An environment is defined through the key at the root level of your
``deploy.conf``::

    #
    # My project's deployment configuration
    #

    production:
      # configure our production deployment

    qa:
      # configure our qa deployment

When you invoke a deployment with ``fab`` you will pass the name of the
environment you want to deploy as the argument to the ``deploy`` task::

    fab deploy:production

Base configuration
------------------
There are some release related configuration values that you must define
at the base of your environment.

* ``git_ref`` - This is the the git reference that will be used for the
  deployment in this environment. It should be fully formed, for example:
  ``refs/remotes/origin/master``. This is required.
* ``keep_releases`` - This should be set to the number of historical releases
  you want to keep on each host. This is optional and defaults to ``10``.
* ``releases_dir`` - This is the file system path that is a directory and will
  hold all of the releases. This is optional and defaults to ``~/releases/``.
* ``current_symlink`` - This is the file system path that garment will use as
  the "current" path. This path will always point to the latest release in the
  releases directory. This is optional and defaults to ``~/current``.


Hosts
-----
Hosts are defined inside an item named ``hosts``` at the root of the
environment configuration. The Host definition is the SSH connection
string used for the host. You must also define their roles::

    # My deployment configuration
    production:
      ...
      hosts:
        username@hostname.domain.tld:
          roles: ['role']

The roles are completely arbitrary and up to you to define and name. We do
recommend the following as standard role names:

* **web** - HTTP(S) server hosts (often only needed in situations where your
  application has specific server configuration requirements that is managed
  by the Garment deployment process)
* **app** - Application server hosts (most typically used role)
* **db** - Database server hosts (needed if migrations or SQL scripts need to
  be run from the local database host)

Variables
---------
You can define variables to be used throughout the configuration. They are
defined in a list and can be built up on top of each other, for example if you
define a variable named ``foo`` you can then reference that variable when you
define the next variable, ``bar``.

Variables are defined under the ``variables`` entry inside an environment::

    # My deployment configuration
    production:
      ...
      variables:
        - foo: 'Hello'
        - bar: '%(foo)s World'
        - baz: '%(bar) from Garment'

``baz`` would be equal to "Hello World from Garment"

As illustrated above you reference variables using the standard Python named
string formatting syntax.

Stages
------
Stages are defined under their **before** and **after** categories. They use
the YAML list of dictionaries syntax where each stage starts with defining a
list and then continues the standard dictionary syntax::

    # My deployment configuration
    production:
      ...
      stages:
        before:
          - id: my_stage
            roles: ['app']
            cd: ~/current/
            commands:
              - prep_environment

          - id: second_stage
            roles: ['app']
            commands:
              - prep_database
              - migrate_database

        after:
          - id: after_stage
            roles: ['app']
            commands:
              - restart_app_server

Each Stage is made up of an ``id``, a list of ``roles`` and a list of
``commands``. Stages can also contain the following extra configuration items:

* **cd** - Change to the specified directory prior to executing the ``commands``
* **prefix** - Prefix a command onto all the other commands, for example you
  could use this to use ``sudo`` to activate a Python virtualenv.
* **shell_env** - A YAML dictionary of items to inject into the shell as
  variables.

Example with all extra items::

    # database migration & static assets
    - id: django
      roles: ['app']
      cd: '%(pythonpath)s'
      prefix: '%(activate)s'
      shell_env:
        PYTHONPATH: '%(pythonpath)s'
        DJANGO_SETTINGS_MODULE: '%(settings)s'
      commands:
        - django-admin.py syncdb
        - django-admin.py migrate
        - django-admin.py collectstatic --noinput
