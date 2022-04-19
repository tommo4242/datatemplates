==============
 Jira Samples
==============

Data Source
============

Internal https://jira.u-blox.net

Template File
=============

.. include:: _templates/jira.tmpl
   :literal:

Loading the Template
====================

.. code-block:: rst

   .. datatemplate:jira:: https://jira.u-blox.net
      :template: jira.tmpl
      :auth: ODY5MjE2MzY0Njc1OiD54YFjaEFimjW1TbvnwC0YzZsw
      :query: project = "Ublox Generic Action Tracker" ORDER BY createdDate ASC

Rendered Output
===============

.. datatemplate:jira:: https://jira.u-blox.net
   :template: jira.tmpl
   :auth: ODY5MjE2MzY0Njc1OiD54YFjaEFimjW1TbvnwC0YzZsw
   :query: project = "Ublox Generic Action Tracker" ORDER BY createdDate ASC
