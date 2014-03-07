.. _configuration:

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


.. _base-configuration:

Base configuration
------------------
There are some release related configuration values that you must define
at the base of your environment.

* ``repo_url`` - This is the git URL that will be used as the ``origin`` for
  the bare repository created on each host. This is required.
* ``git_ref`` - This is the git reference that will be used for the deployment
  in this environment. A branch or tag, for example: ``master``. This is
  required.
* ``deploy_dir`` - This is the base directory that should be used for all of
  the deployment directories. Example: ``/home/user/deploy``. This is required.
* ``source_dir`` - This holds the checked out git repository. This is optional
  and defaults to ``{deploy_dir}/source``.
* ``releases_dir`` - This is the file system path that is a directory and will
  hold all of the releases. This is optional and defaults to
  ``{deploy_dir}/releases/``.
* ``current_symlink`` - This is the file system path that garment will use as
  the "current" path. This path will always point to the latest release in the
  releases directory. This is optional and defaults to
  ``{deploy_dir}/current``.
* ``keep_releases`` - This should be set to the number of historical releases
  you want to keep on each host. This is optional and defaults to ``10``.


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

The roles are completely arbitrary and up to you to define and name in what
ever way suits your project. They are used in the Stages below to target which
hosts the each stage should run on.


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
        - bar: '{foo} World'
        - baz: '{bar} from Garment'

``baz`` would be equal to "Hello World from Garment"

As illustrated above you reference variables using the standard Python named
string formatting syntax. Each variable is passed all previous variables as
keyword args using the Python string `.format() method`_.

Stages
------
Stages are defined under the **before**, **after** and **rollback** categories.
They are all optional.

They use the YAML list of dictionaries syntax where each stage starts with
defining a list and then continues the standard dictionary syntax::

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


.. _.format() method: http://docs.python.org/2/library/string.html#format-string-syntax
