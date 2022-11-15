# MIDI melody similarity backend
Django backend for VMM semestral work

### Requirements
Python >=3.11, venv, pip

## Project setup

Create a new virtual environment using `venv`

```sh
python3 -m venv venv
```

Activate the new virtual environment

```sh
source venv/bin/activate
```

Install packages with `pip`

```sh
pip install -r requirements.txt
```

Execute db migrations

From `/backend` directory:
```sh
python manage.py migrate
```

Generate melodies to database (piano-midi.de)
```sh
python manage.py shell
```
```python
from api.melody_utils.generator import generate_all_piano_midi_de
generate_all_piano_midi_de()
```

## Run server
From `/backend` directory:

```sh
python manage.py runserver
```