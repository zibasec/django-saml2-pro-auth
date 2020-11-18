from glob import glob

certfile = "certs/cert.pem"
keyfile = "certs/key.pem"
reload = True
reload_extra_files = glob("*.py") + glob("*.html")
