How to get list of services with Python wrapper?
------------------------------------------------

This documentation will help you to list your services at ovh.

## Requirements

- Having an OVH Account with services inside

## Install Python wrapper

The easiest way to get the latest stable release is to grab it from pypi using ```pip```.

```bash
pip install tabulate ovh
```

## Create a new token

You can create a new token using this url: [https://api.ovh.com/createToken/?GET=/*](https://api.ovh.com/createToken/?GET=/*).
Keep application key, application secret and consumer key and replace default values in ```ovh.conf``` file.

```ini
[default]
; general configuration: default endpoint
endpoint=ovh-eu

[ovh-eu]
; configuration specific to 'ovh-eu' endpoint
application_key=my_app_key
application_secret=my_application_secret
; uncomment following line when writing a script application
; with a single consumer key.
consumer_key=my_consumer_key
```

Be warned, this token is only valid to get informations of your OVH services. You cannot changes or delete your products with it.
If you need a more generic token, you may adjust the **Rights** fields at your needs.

## Download the script

- Download and edit the python file to get service that will expired. You can download [this file](serviceList.py).

## Run script

```bash
python serviceList.py
```

For instance, using the example values in this script, the answer would look like:
```bash
Type                     ID                                status    expiration date
-----------------------  --------------------------------  --------  -----------------
cdn/webstorage           cdnstatic-no42-1337               ok        2016-02-14
cloud/project            42xxxxxxxxxxxxxxxxxxxxxxxxxxx42   expired   2016-01-30
hosting/privateDatabase  no42-001                          ok        2016-02-15
license/office           office42.o365.ovh.com             ok        2016-02-15
router                   router-rbx-1-sdr-1337             expired   2016-01-31
```

## What's more?

You can discover all OVH possibilities by using API console to show all available endpoints: [https://api.ovh.com/console](https://api.ovh.com/console)

