Changelog
=========

## 0.3.1 (2014-12-22)

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
