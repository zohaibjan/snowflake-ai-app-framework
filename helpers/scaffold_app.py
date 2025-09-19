#!/usr/bin/env python3
"""
Scaffold a new app from the framework template.

Usage:
  python helpers/scaffold_app.py my-new-app

This will copy apps/app-template to ../apps/my-new-app and replace placeholders.
"""
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / 'apps' / 'app-template'
TARGET_ROOT = ROOT.parent / 'apps'

REPLACEMENTS = [
    ('{{APP_NAME}}', None),
    ('{{app_name}}', None),
]


def replace_in_file(path: Path, replacements):
    text = path.read_text(encoding='utf-8')
    for old, new in replacements:
        text = text.replace(old, new)
    path.write_text(text, encoding='utf-8')


def main():
    if len(sys.argv) < 2:
        print('Usage: python helpers/scaffold_app.py <app-name>')
        sys.exit(1)

    app_name = sys.argv[1]
    if not re.fullmatch(r'[a-zA-Z0-9_-]+', app_name):
        print('Error: app-name must match [a-zA-Z0-9_-]+')
        sys.exit(1)

    # Compute names
    app_name_slug = app_name.lower().replace('-', '_')
    app_name_title = re.sub(r'[_-]+', ' ', app_name).title().replace(' ', '')

    target_dir = TARGET_ROOT / app_name
    if target_dir.exists():
        print(f'Error: target app directory already exists: {target_dir}')
        sys.exit(1)

    # Copy template
    print(f'Copying template to {target_dir}...')
    shutil.copytree(TEMPLATE, target_dir)

    # Prepare replacements
    replacements = [
        ('{{APP_NAME}}', app_name_title),
        ('{{app_name}}', app_name_slug),
    ]

    # Replace placeholders in files
    for path in target_dir.rglob('*'):
        if path.is_file():
            try:
                replace_in_file(path, replacements)
            except UnicodeDecodeError:
                # Skip binary files
                pass

    print('Done! Next steps:')
    print(f'  1) cd {target_dir}')
    print('  2) Review README.md and settings')
    print('  3) Commit and push to trigger deployment workflows')


if __name__ == '__main__':
    main()
