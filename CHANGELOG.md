Changelog
=========

## 1.1.0 (2023-04-07)

- [feature]: add support for v2 routes (#115)
- [buildsystem]: move to github actions, using unittest (#112, #114, #117, #113)

## 1.0.1 (2023-03-07)

- [buildsystem] missing changelog entry for 1.0.0
- [buildsystem] add github actions
- [buildsystem] apply flake8 linting
- [buildsystem] apply isort formatting
- [buildsystem] apply black formatting
- [buildsystem] switch to pytest

## 1.0.0 (2022-03-15)

- [buildsystem] remove python 2 support (#110)
- [buildsystem] added compatibility for Python 3.8, 3.9, 3.10 (#108)
- [feature] add headers customisation in `raw_call` (#84)
- [fix] do not send JSON body when no parameter was provided (#85)
- [buildsystem] improved coverage and bump coverage library (#100)
- [buildsystem] add scripts for debian packaging (#110)

## 0.6.0 (2022-03-15)

 - [compatibility] add support for Python 3.10
 - [dependencies] drop vendored requests library, added requests>=2.11.0
 - [fix] previous 'disable pyopenssl for ovh to fix "EPIPE"' fix is handled
   by requests dependency update

## 0.5.0 (2018-12-13)
 - [compatibility] drop support for EOL Python 2.6, 3.2 and 3.3 (#71)
 - [feature] Add OVH US endpoint (#63 #70)
 - [buildsystem] auto Pypi deployment when new tag (#60)
 - [documentation] fix typos (#72)
 - [documentation] flag package as Stable (#59)

## 0.4.8 (2017-09-15)
 - [feature] Add ResourceExpiredError exception (#48)

## 0.4.7 (2017-03-10)
 - [api] add raw_call method returning a raw requests Response object
 - [documentation] add advanced usage documentation
 - [buildsystem] fix bump-version debian/Changelog generation

## 0.4.6 (2017-02-27)
 - [api] add query_id property to exceptions to help error reporting
 - [api] remove deprecated runabove api
 - [feature] remove Python SNI warnings, OVH API does not need SNI (#35)
 - [buildsystem] Add build dependency on python3-setuptool
 - [buildsystem] Add debian folder

## 0.4.5 (2016-07-18)
 - [fix] (regression) body boolean must be sent as boolean (#34)

## 0.4.4 (2016-07-15)
 - [buildsystem] fix PyPi upload

## 0.4.3 (2016-07-15)
 - [api] fix: api expects lower case boolean value in querystring. Closes #32 (#33)
 - [feature] Add response in exception (#30, #31)
 - [feature] Read custom file on runtime (#29)
 - [buildsystem] chore: use find_packages in setup.py instead of hard-coded list
 - [buildsystem] fix: drop conflicting d2to1 dependency (closes #25 closes #27)
 - [documentation] improv contributing guide (#26)

## 0.4.2 (2016-04-11)
 - [buildsystem] fix missing cacert.pem file in package. Closes #23

## 0.4.1 (2016-04-08)
 - [buildsystem] fix: include the vendorized packages and package data in the install process (#22)
 - [buildsystem] add python 3.5 support
 - [documentation] add license information to README

## 0.4.0 (2016-04-07)
 - [feature] add consumer key helpers
 - [fix] disable pyopenssl for ovh to fix "EPIPE"
 - [buildsystem] vendor 'requests' library to fix version and configuration conflicts
 - [buildsystem] add 'scripts' with release helpers
 - [documentation] add consumer_key documentation
 - [documentation] fix rst format for pypi
 - [documentation] add service list example
 - [documentation] add expiring service list example
 - [documentation] add dedicated server KVM example
 - [documentation] explicitly list supported python version

## 0.3.5 (2015-07-30)

 - [enhancement] API call timeouts. Defaults to 180s
 - [buildsystem] move to new Travis build system
 - [documentation] send complex / python keyword parameters

## 0.3.4 (2015-06-10)

 - [enhancement] add NotGrantedCall, NotCredential, Forbidden, InvalidCredential exceptions

## 0.3.3 (2015-03-11)

 - [fix] Python 3 tests false negative
 - [fix] More flexible requests dependency

## 0.3.2 (2015-02-16)

 - [fix] Python 3 build

## 0.3.1 (2015-02-16)

 - [enhancement] support '_' prefixed keyword argument alias when colliding with Python reserved keywords
 - [enhancement] add API documentation
 - [enhancement] Use requests Session objects (thanks @xtrochu-edp)

## 0.3.0 (2014-11-23)
 - [enhancement] add kimsufi API Europe/North-America
 - [enhancement] add soyoustart API Europe/North-America
 - [Q/A] add minimal integration test

## 0.2.1 (2014-09-26)
 - [enhancement] add links to 'CreateToken' pages in Readme
 - [compatibility] add support for Python 2.6, 3.2 and 3.3

## 0.2.0 (2014-09-19)
 - [feature] travis / coveralls / pypi integration
 - [feature] config files for credentials
 - [feature] support ``**kwargs`` notation for ``Client.get`` query string.
 - [enhancement] rewrite README
 - [enhancement] add CONTRIBUTING guidelines
 - [enhancement] add MIGRATION guide
 - [fix] workaround ``**kwargs`` query param and function arguments collision

## 0.1.0 (2014-09-09)
 - [feature] ConsumerKey lifecycle
 - [feature] OVH and RunAbove support
 - [feature] OAuth 1.0 support, request signing
