#!/bin/sh

source venv/scripts/activate
cd code
python read_and_plot.py
$SHELL