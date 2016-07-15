Changelog
=========

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
 - [docuumentation] add service list example
 - [documentation] add expiring service list example
 - [documentation] add dedicated server KVM example
 - [documentation] explicitely list supported python version

## 0.3.5 (2015-07-30)

 - [enhancement] API call timeouts. Defaults to 180s
 - [buildsystem] move to new Travis build system
 - [documentation] send complex / python keywork parameters

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
