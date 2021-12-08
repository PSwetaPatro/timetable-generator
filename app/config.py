import os
import secrets

from flask import current_app, request

static_path = os.path.normpath(current_app.root_path)
static_path = os.sep.join(os.path.split(static_path)[:-1])


class Config:
    SECRET_KEY = secrets.token_hex(8)
    OUTPUT_DIR = os.path.join(static_path, "output")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    json_indent = 4


conf = Config()
