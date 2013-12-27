Garment documentation
=====================

A collection of fabric_ tasks that roll up into a single deploy function. The
whole process is coordinated through a single deployment configuration file
named ``deploy.conf``

Garment was written to be flexible enough to deploy any network based
application to any number of hosts, with any number of roles, yet still provide
a convention for the deployment process and take care of all of the routine
tasks that occur during deployment (creating archives, maintaining releases,
etc).

Currently Garment only supports applications that use GIT as their SCM, but it
could easily be extended to support others.

Contents:

.. toctree::
   :maxdepth: 2

   strategy.rst
   configuration.rst
   vagrant.rst

.. _fabric: http://fabfile.org/
