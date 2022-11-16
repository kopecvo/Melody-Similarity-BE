# MIDI melody similarity backend
Django backend for VMM semestral work

### Requirements
Python 3, venv, pip

## Project setup

Create a new virtual environment using `venv`

```sh
python -m venv venv
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
(or use a Django Jupyter notebook)

## Run server
```sh
python manage.py runserver
```

## Django integrated Jupyter notebooks

* Must be run from Django root directory (preferably `/notebook`), otherwise Django won't work
* Use Django Shell-Plus kernel
  * `python manage.py shell_plus --notebook` to start the kernel
* `import django_initiliaser` to setup the notebook