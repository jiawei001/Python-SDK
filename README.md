# Knurld SDK for Python

A Python SDK for integrating with [knurld API v1.](https://developer.knurld.io/developer-guide) Compatible with Python 2.7.
Documentation available here: [Knurld SDK Documentation](https://github.com/rohansb/knurld_sdk/blob/master/knurld_sdk/_doc_root.rst)

## Register
If you haven't already registered for your knurld developer account, you can get started here: [Register](https://developer.knurld.io/) to get you the appropriate credentials for using the APIs.

## Setup

To get started, you can install this package from the root directory by running:

`$ python setup.py install` (to use the knurld_sdk as is) or

`$ python setup.py develop` (if you want to make changes to your local copy of knurld_sdk and have them directly reflect in your app; using symlinks)

After installation, first step is setup your [config.cfg](https://github.com/rohansb/knurld_sdk/blob/master/knurld_sdk/config.cfg) and substitute the fields with your credentials and preferences.

You must setup: PROJECT_ROOT, CLIENT_ID, CLIENT_SECRET and DEVELOPER_ID fields.
It is advisable not to make changes to the URL_* fields for at least the v1 of the knurld APIs.

This is a one time setup!

Once you have it, open a Python console or a python module in your app, write:

```
from knurld_sdk.APIManager import TokenGetter
tg = TokenGetter()
token = tg.get_token()
```

Likewise, you can access all other classes from the APIManager.

## Tests
You may run the tests using pre-configured `nosetests` for ease of use. E.g.
`nosetests --nocapture tests/TestAPIManager.py:TestTokenGetter.test_get_token`

You may want to see the test coverage report in the documentation: {TODO link to test coverage report}

## Uploader
You will need to upload and host your audio .wav files. For now this SDK has a helper module [Dropbox.py](https://github.com/knurld/Python-SDK/blob/master/knurld_sdk/uploader/Dropbox.py) for hosting your files on DropBox, which wraps the [Dropbox SDK.](https://www.dropbox.com/developers-v1/core/start/python)

## Packaging
This software is packaged using the standard procedure mentioned in the [python-packaging doc.](https://python-packaging.readthedocs.org/en/latest/minimal.html)

## License
You may read [License](https://github.com/rohansb/knurld_sdk/blob/master/LICENSE) agreement for using this software.
