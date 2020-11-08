# Example Django App

SAML2 Authentication Django Demo

---

## Installation

Setup a virtual environment and activate it:

```sh
python -m venv venv
source venv/bin/activate
```

Install the dependencies. This will install an editable version of the django-saml-pro-auth package one directory up.

```sh
pip install -r requirements.txt
```

Update the values in `example/settings.py` and be sure to configure the `SAML_PROVIDERS` and `SAML_USERS_MAP`. Two examples have been included for reference.

Configure your IdP with the relevant settings.

**NOTE:** This will work with `http` or `https://127.0.0.1/` should work fine for testing in your IdP.

Migrate and create the cache table if you are using the database cache backend.

```sh
python manage.py migrate
python manage.py createcachetable
```

Create a user in the database with an email or username attribute that matches an attribute in your IdP so you can test the full login flow.

Run the server. You don't need to use `gunicorn` but this allows us to run the server with self-signed certificates so that some IdP's (GSuite and others) don't complain.

```sh
gunicorn example.wsgi --conf gunicorn.conf.py
```
