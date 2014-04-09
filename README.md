D-PLACE
=============
[![Build Status](https://travis-ci.org/NESCent/dplace.svg?branch=master)](https://travis-ci.org/NESCent/dplace)

This repository contains a [GeoDjango](http://geodjango.org) application for the NESCent working group [Explaining cultural diversity: A new evolutionary synthesis](http://evolutionary-synthesis.wikispaces.com) (wiki login required)

So far, the main focus of development has been

1. [data models](dplace_app/models.py)
2. [CSV import scripts](dplace_app/load.py)
3. [REST API](dplace_app/api_views.py)

Additional prototypes are under dvelopment for HTML-based [geographic search](dplace_app/views.py) and [AngularJS](http://angularjs.org) user interfaces.

For easy installation of a development VM using [Vagrant](http://vagrantup.com), please see [dplace-vagrant](https://github.com/dleehr/dplace-vagrant)
