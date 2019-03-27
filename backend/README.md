# BirdStats Flask Backend

The backend for this project is a simple python Flask API server.

It has minimal requirements and is simply intended to provide some basic data to the reasonably static front end.

Ordinarily I would use something like Connexion to enforce the API, but given my limited time, this is a basic API implementation.

You can view an example of partial specification of the API under the spec directory.

## Installation

To install the backend, assuming you are running a POSIX compliant (or near to) operating system with Python 2.7 and virtualenv installed:

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

Then, to run the backend with defaults (for a demo):
```bash
# assuming you sourced the virtualenv already
python src/app.py
```
