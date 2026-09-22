#!/usr/bin/env python3
"""Compatibility entry point: the installation is handled by Calamares."""
import os
import sys

os.execv('/usr/bin/katu-installer', ['katu-installer', *sys.argv[1:]])
