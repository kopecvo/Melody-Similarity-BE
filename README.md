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

## Run server
From `/backend` directory:

```sh
python manage.py runserver
```

## Extracting melodies
1) Add MIDI file to `/backend/midi`
2) Access shell
    ```shell
    python manage.py shell
    ```
3) 
    ```python
    from melody_extractor.extractor import get_highest_melody
    get_highest_melody("midi/{file}", [{tracks to merge}], 10)
    ```