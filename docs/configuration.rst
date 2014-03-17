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


Extending items
---------------
Often times when building deployment configurations you will find yourself
repeating the same variables & stages. Garment configuration allows for one
environment to extend another through the use of the ``extends`` keyword so
that you can leverage reusability to keep your configuration concise and error
free.

Complete Django Example::

    #
    # Deployment configuration
    #

    staging:
      forward_agent: True
      repo_url: git@myhost.tld:myrepo.git
      git_ref: develop
      deploy_dir: /home/staging/deploy
      keep_releases: 3

      hosts:
        staging@myhost.tld:
          roles: ['app']

      variables:
        - home: '/home/staging'
        - virtualenv: '{home}/virtualenv'
        - activate: 'source {virtualenv}/bin/activate'
        - pythonpath: '{current_symlink}/myapp'
        - settings: 'myapp.settings.staging'
        - logdir: '{home}/logs/application/'

      stages:
        before:
          - id: dirs
            roles: ['app']
            commands:
              - 'mkdir -p {logdir}'

          - id: virtualenv
            roles: ['app']
            commands:
              - '[ ! -d {virtualenv} ] && virtualenv {virtualenv} || echo "virtualenv exists"'
              - 'rm -f virtualenv/lib/*/no-global-site-packages.txt'

          - id: install
            roles: ['app']
            prefix: '{activate}'
            shell_env:
              PYTHONPATH: '{pythonpath}'
              DJANGO_SETTINGS_MODULE: '{settings}'
            commands:
              - 'pip install -r {release_dir}/requirements/production.txt'
        
          - id: django
            roles: ['app']
            prefix: '{activate}'
            shell_env:
              PYTHONPATH: '{pythonpath}'
              DJANGO_SETTINGS_MODULE: '{settings}'
            commands:
              - django-admin.py syncdb
              - django-admin.py migrate
              - django-admin.py collectstatic --noinput

        after:
          - id: restart
            roles: ['app']
            prefix: '{activate}'
            commands:
              - 'supervisorctl restart gunicorn'


    preview:
      extends: staging

      deploy_dir: /home/preview/deploy

      hosts:
        preview@my-host.tld:
          roles: ['app']

      variables:
        - home: '/home/preview'
        - settings: 'myapp.settings.preview'

      stages:
        after:
          - id: contrived
            roles: ['app']
            commands:
              - 'echo "Just a silly example"'

          - id: restart
            roles: ['app']
            prefix: '{activate}'
            commands:
              - 'supervisorctl restart gunicorn'
              - 'echo "PREVIEW HAS BEEN RESTARTED"'


Here you can see that the ``preview`` environment has specified
``extends: staging`` as an option. When the configuration loader sees this it
will merge the configuration from the ``preview`` environment together with
the ``staging`` environment. 

The ``hosts`` are not copied during the merge so you **always** need to specify
hosts in an extended environment.

The ``variables`` and ``stages`` are fully merged in the same order. That means
if you have a variable named ``home`` in the base environment and its the 2nd
variable defined when the ``home`` variable from the new extended environment
is merged in it will also been the 2nd variable defined when the variable
resolution is applied to the configuration. Anything defined in an extended
environment that is not defined in a base environment will be appended. In the
above example it means that even though the ``contrived`` step was defined
before the ``restart`` step when the config is fully resolved the ``contrived``
step will actually run after the ``restart`` step because the ``restart`` step
overrode the restart step from the ``staging`` environment.

The above example shows two extra steps being added to the ``after`` stage, but
in reality they are not needed and have been added purely to explain how the
config loaded merges items. If you remove the two extra steps you can see that
the configuration for preview becomes quite concise, less than 10 lines.

.. _.format() method: http://docs.python.org/2/library/string.html#format-string-syntax
