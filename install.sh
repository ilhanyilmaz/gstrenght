#!/bin/sh

- py m pip install --user virtualenv
- mkdir Projects
- cd Projects
- cd gstrenght
- virtualenv venv
- .\venv\Scripts\activate
- cd code
- pip install -r requirements.txt