#!/bin/bash
gunicorn --chdir . app:app --bind 0.0.0.0:8000
