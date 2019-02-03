###########
Development
###########

Issues and pull requests are welcome at `GitHub`_. Please be sure to add or update the documentation appropriately along with your code changes.


************************
Style checks and testing
************************

Any pull requests will be validated with `Travis CI`__, but you may run the tests locally with `tox`_ and/or `poetry`_. We use ``tox`` to wrap ``poetry`` commands in our Travis CI configuration.

Run the entire suite of tests:

.. code-block:: bash
  :caption: **Using tox**

  tox

Or just run one off tests:

.. code-block:: bash
  :caption: **Using poetry**

  # Install the project dependencies, including dev-dependencies into a
  # poetry-managed virtual environment.
  poetry install -E jwt -E fernet

  # Run the individual test commands as needed in the virtual environment
  poetry run pytest -v tests
  poetry run flake8 falcon_epdb tests
  poetry run pylint falcon_epdb
  poetry run pydocstyle falcon_epdb tests

  # Build the docs and find them in docs/_build
  poetry run sphinx-build -b html docs docs/_build


*******************
Adding dependencies
*******************

Use the ``poetry add`` command to add dependencies to the ``pyproject.toml`` file.

.. code-block:: bash
  :caption: **Using poetry add**

  poetry add cryptography
  poetry add --dev coveralls


************************
Publishing a new release
************************

The project is configured to publish a release anytime a tag is pushed to the GitHub repository and the build succeeds. The tagging convention is ``v<Major>.<minor>.<patch>``, and it should follow `semver`_ conventions. One can bump the version using the `poetry version`__ command.

When creating a release, ensure the following:

  - The documentation is up to date with the new changes.
  - The changes have been noted in the CHANGELOG.rst.
  - The build "badges" are all passing. The readthedocs one seems somewhat finicky these days.
  - The version has been incremented accordingly.


.. Links
__ Travis_CI_

.. _Travis_CI: https://travis-ci.org/jcwilson/falcon-epdb

.. _GitHub: https://github.com/jcwilson/falcon-epdb

.. _tox: https://tox.readthedocs.io

.. _poetry: https://poetry.eustace.io/

.. _semver: https://semver.org/

__ poetry_version_

.. _poetry_version: https://poetry.eustace.io/docs/cli/#version
