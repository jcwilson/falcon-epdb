#########
Changelog
#########

******
v1.1.0
******

Cleanup and more tooling
========================
* Removed the ``__version__`` attribute. It's unnecessary and adds fragile manual maintenance overhead.

  * This would normally be considered a breaking change, but I'm pretty sure no one's using this yet, much less depending on that attribute being present

* Added the ``black`` code formatter to the development stack

  * Applied it to both code and tests
  * Mostly just converted all strings to double-quotes
  * Removed ``pylint-quotes`` now that ``black`` has been added

* Added source code link and badge to ``README.rst`` for easier navigation from readthedocs.io
* Switched ``pip_install`` to ``false`` in ``readthedocs.io``
* Added documentation around the style-enforcement tools and other conventions
* Cleaned up some documentation
* Added several project url attributes to ``pyproject.toml`` in the hopes that poetry and PyPI will display the relative links on the project page.


******
v1.0.0
******

Initial release
===============
* Add support for Fernet backend
* Add support for JWT backend
