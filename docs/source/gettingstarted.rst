Getting Started
===============

Requirements
------------

* Python >= 3.5, pip
* Dependencies:

    .. literalinclude:: ../../requirements.txt

Installing Magepy
-----------------

Mage can be installed with a simple ``pip install magepy``.  Here is an example of installing it in an Ubuntu 16 docker container:

.. code-block:: bash

    docker run -it --rm ubuntu:16.04
    apt update && apt install python3 python3-pip
    pip3 install magepy


Configuring the environment
---------------------------

Magepy requires the following information to connect to the `Mage monitoring service <https://mage.stage2sec.io/>`_.  Contact magepy@stage2sec.com for the correct values:

* COGNITO_USERNAME=Cognito username
* COGNITO_PASSWORD=Cognito Password
* GQL_URL=Mage endpoint URL
* POOL_ID=AWS pool ID
* CLIENT_ID==AWS client ID

These values can be supplied either via environment variable or environment file.  The Cognito username and password may be entered manually at runtime if desired.

The following places are checked for this connection information:

* ~/.env
* ./.env
* filename passed into `mage.connect`


Connecting to Mage
------------------

Connecting to Mage is as simple as calling `mage.connect`::

    import mage
    mage.connect()

.. warning:: The session created by `mage.connect` expires after one hour.  If you need a longer session than this then you need to call `mage.connect` again to reestablish the connection.

Creating an assessment
----------------------

In order for Mage to scan your assets, you'll need to define what you want assessed.  This is known as an assessment.  Assessments are created by calling :meth:`mage.Assessment.create() <mage.api_resources.assessment.Assessment.create>`::

    assessment = mage.Assessment.create('EXTERNAL', name='Public Webservers')


Creating and adding assets to assessments
-----------------------------------------

An asset is a specific item to test such as an IP address/CIDR, hostname, or domain name.  Assets can be associated with more than one assessment.  When an assessment is run it checks the assets associated with that assessment.  Assets are created by calling :meth:`mage.Asset.create() <mage.api_resources.asset.Asset.create>`::

    asset = mage.Asset.create('DOMAIN', 'www.example.com')

.. warning::
    Currently, it is possible to create an asset multiple times, which may cause confusion later on.  Ensure you only call create for assets that do not already exist.

To add an asset to an assessment call `Assessment.connect` or `Asset.connect`::

    assessment.connect(asset)
    asset.connect(assessment)

To simplify adding assets to assessments, you can also bulk load them in using `load_assets`.  This method only creates an asset if it does not already exist.::

    assessment.load_assets('webservers.json')

Refer to `load_assets` for supported JSON syntax.


Adding credentials
------------------

Credentials are needed for testing the security of cloud deployments.  These can be created and associated with assessments by calling `mage.CloudCredential.create <cloud_credential.CloudCredential.create>`.


Running an assessment
---------------------

Once an assessment is defined with assets added, it can be run once by calling :meth:`mage.Assessment.start <mage.api_resources.assessment.Assessment.start>`::

    assessment_run_id = assessment.start()


Scheduling an assessment
------------------------

Assessments may be automatically run multiple times according to a set schedule.  Assessments can be scheduled by calling :meth:`mage.Assessment.create_schedule <mage.api_resources.assessment.Assessment.create_schedule>`::

    assessment.create_schedule('DAILY', {'hour':'23', 'minute':'55'})


Reviewing assessment results
----------------------------

Assessments take time to run.  You can check the status of an assessment by querying the :attr:`~mage.api_resources.assessment_run.AssessmentRun.status` attribute.  Note that results are cached locally, so if you already have an AssessmentRun instance you will need to `refresh` the data from the server.

.. code-block::

    # Get the assessment's last run
    assessment_run = assessment.runs_filter.last()[0]

    count = 0
    while assessment_run.state not in ['COMPLETE', 'FAILED', 'CANCELED']:
        print('.')
        time.sleep(60)
        count += 1

        # make sure we have a valid access token by refreshing every 30 minutes
        if count == 30:
            mage.connect()

        assessment_run.refresh('state')

    # if it is complete then get the report url
    if assessment_run.state == 'COMPLETE':
        report_url = assessment_run.report_url
        print(report_url)
    else:
        print("Run status is", assessment_run.state)

Besides retrieving the report PDF to review, you can also query the results directly from python.  The results are lumped into several categories such as `mage.Finding <finding.Finding>`, `mage.Lead <lead.Lead>`, and `mage.TTP <ttp.TTP>` (Tactics, Techniques, and Procedures).  You can iterate through these as follows.

.. code-block::

    for finding in assessment_run.findings.auto_paging_iter():
        print("Finding %s (%s) - %s" % (finding.id, finding.affected_asset.asset_identifier, finding.title))

    for lead in assessment_run.leads.auto_paging_iter():
        print("Lead %s - %s" % (lead.id, lead.title))

    for ttp in assessment_run.ttps.auto_paging_iter():
        print("TTP %s - %s" % (ttp.id, ttp.technique))


Tips and Tricks
===============

Selecting results
-----------------

A normal query to find an assessment by name may look like::

    mage.Assessment.eq(name="MyTest").list()[0]

As a shortcut you may instead specify::

    mage.Assessment.eq(name="MyTest")[0]

and the implied `list <ListableAPIResource.list>` or `search <ListableAPIResource.search>` method will be selected for you.


Modifying results
-----------------

Assume you accidentally created an assessment without a name.  You can update the name with a simple assignment.  The value will be automatically updated on the server::

    import mage
    mage.connect()
    assessment = mage.Assessment.create('EXTERNAL')
    assessment.name = 'My New Assessment'


Iterating through results
-------------------------

In order to not waste resources, queries to the server only return a limited amount of information (e.g., 100 records) in the form of a `ListObject` instance.  You can manually retrieve more records by calling `ListObject.next_page` to get the next set of results.

You can also iterate through the results.

.. code-block::

    # Iterate through just the local results
    for finding in assessment_run.findings:
        print("local finding", finding.id)

    # Iterate through all results
    for finding in assessment_run.findings.auto_paging_iter():
        print("all findings", finding.id)

If you prefer to always iterate through all records you can set `mage.auto_page` to True.

.. code-block::

    import mage
    mage.connect()

    # set the auto_paging to get all records
    mage.auto_page = True

    # These two for loops are now equivalent:

    # Iterate through just the local results
    for finding in assessment_run.findings:
        print("local finding", finding.id)

    # Iterate through all results
    for finding in assessment_run.findings.auto_paging_iter():
        print("all findings", finding.id)


You can additionally iterate over whole sets of data::

    for assessment in mage.Assessment:
        print(assessment.name)

Raw Queries
-----------

If for some reason you need to hand craft a query to the server you can do that with `mage.query <mage.query.query>` and `mage.mutate <mage.query.mutate>`::

    import mage
    mage.connect()
    mage.query("listAssessments {items {id}, nextToken}")


Debugging
---------

You can enable debug output by setting the log level to 'DEBUG'::

    import mage, logging
    logging.basicConfig()
    mage.logger.setLevel('DEBUG')
