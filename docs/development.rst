###########
Development
###########

Issues and pull requests are welcome at `GitHub`_. Please be sure to add or update the documentation appropriately along with your code changes.


************************
Style checks and testing
************************

All pull requests will be validated with `Travis CI`__, but you may run the tests locally with `tox`_ and/or `poetry`_. We use ``tox`` to wrap ``poetry`` commands in our Travis CI configuration.

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

  # Run the individual style checks as needed in the virtual environment
  poetry run black --check falcon_epdb
  poetry run flake8 falcon_epdb tests
  poetry run pylint falcon_epdb
  poetry run pydocstyle falcon_epdb tests

  # Run the unit tests in the virtual environment
  poetry run pytest -v tests

  # Build the docs and find them in docs/_build
  poetry run sphinx-build -b html docs docs/_build


Style
=====

Conventions
-----------
No new-lines in paragraphs in ``*.rst`` documents to manage line-length. It's too much trouble to add line breaks manually at some arbitrary cut-off point. Your editor should word wrap for you. However, doc-comments in the code should respect the Python file line length.

Tools
-----
This project uses several tools to ensure quality and consistency.

git-hooks (optional, but recommended)
.....................................
`git-hooks`__ instructs git to look in the src-controlled ``.githooks/`` directory for any git hook scripts. We use it to automatically apply the `black`_ formatter during the ``pre-commit`` checks.

The ``git-hooks`` tool offers other functionality such as global hooks, running individual hooks manually and piecemeal disabling of hooks. It's worth checking out for your other projects, too. *Full disclosure, I'm also the author of that tool.*

black
.....

This is an `opinionated code formatter`__. This is the first thing we check against, as this potentially modifies the code and we wish that the new code remains compliant with the subsequent checks.

While we use it to verify compliant formatting, it is recommended that you install it as a global tool on your own system and apply the auto-formatting prior to commiting your code. It already has out-of-the-box integrations with several popular editors.

If you do not wish to install globally on your system, you can still install it in the ``poetry``-managed virtual environment:

.. code-block:: bash

  # Install black unmanaged by poetry in order to get around
  # impossible version requirements.
  poetry run pip install black

  # Run the formatter; will modify files
  poetry run black falcon_epdb tests

flake8
......
This is the popular PEP8 tool with a few more improvements.

pylint
......
The comprehensive, fairly opinionated code quality tool. It generates a score (on a scale of 0 to 10) based on a multitude of criteria. This project has a minimal list of disabled rules, which are disabled to support Python 2.7 support.

pydocstyle
..........
Even documentation needs to set a high bar. Much of the inline doc-comments become part of the auto-generated API documents. This ensures consistency of form as well as of content.


*******************
Adding dependencies
*******************

Use the ``poetry add`` command to add dependencies to the ``pyproject.toml`` file.

.. code-block:: bash
  :caption: **Using poetry add**

  poetry add cryptography
  poetry add --dev coveralls

.. note:: If you add a non-dev dependency, be sure to also add it to requirement-docs.txt.

************************
Publishing a new release
************************

The project is configured to publish a release anytime a tag is pushed to the GitHub repository and the build succeeds. The tagging convention is ``v<Major>.<minor>.<patch>``, and it should follow `semver`_ conventions. One can bump the version using the `poetry version`__ command.

When creating a release, ensure the following:

  - The documentation is up to date with the new changes.
  - The changes have been noted in the CHANGELOG.rst.
  - The build "badges" are all passing.
  - The version has been incremented accordingly.


.. Links
__ Travis_CI_

.. _Travis_CI: https://travis-ci.org/jcwilson/falcon-epdb

__ git_hooks_

.. _git_hooks: https://github.com/fivestars/git-hooks

__ opinionated_code_formatter_

.. _opinionated_code_formatter: https://black.readthedocs.io/en/stable

.. _GitHub: https://github.com/jcwilson/falcon-epdb

.. _tox: https://tox.readthedocs.io

.. _poetry: https://poetry.eustace.io/

.. _semver: https://semver.org/

__ poetry_version_

.. _poetry_version: https://poetry.eustace.io/docs/cli/#version
