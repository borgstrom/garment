.. _usage:

Using Garment
=============
Garment is a library of tasks to be used from within a `Fabric file`_.


Installing Garment
------------------
To install garment we recommend using pip to install it into a virtualenv::

    pip install garment

Once installed you will be able to use garment in your ``fabfile.py``


Creating the Fabric file
------------------------
At the root of your project create a file named ``fabfile.py`` and add the
following line to it::

    from garment import *

You can now add any other tasks you want into your ``fabfile.py`` file, using
all the power of Fabric.


Create your configuration
-------------------------
See the :ref:`strategy` documentation to understand how garment approaches the
deployment process and then see the :ref:`configuration` documentation for
information on how to build a configuration.


Deploying your application
--------------------------
Now that you have installed, setup and configured garment you can use Fabric
to run a deployment. Let's say you wanted to deploy to staging, you would
run::

    deploy staging

The above uses the ``deploy`` script we ship with garment. You can also invoke
Fabric directly::

    fab deploy:staging


Runtime commands
----------------
Garment provides a number of functions for managing your project's deployment,
to see all of them ask Fabric for a list::

    fab -l


Including or Excluding steps
----------------------------
Sometimes you may want to only run some of the steps in your deployment. For
example, perhaps you're iterating over a new piece of functionality and want
to share your designs with other team members but these changes don't require
anything other than deploying the files (ie. you can skip the DB migrations,
environment update, requirement installation, etc). To accomplish this you can
use either the ``include`` or ``exclude`` parameters to the ``deploy``
function. They are mutually exclusive and you can only use one of them.

Both ``include`` and ``exclude`` take a comma separated list of step ids. As
Fabric also uses commas you must quote & escape them::

    fab deploy:staging,exclude='virtualenv\,install\,django_db'
