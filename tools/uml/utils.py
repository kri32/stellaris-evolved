import codecs
import os
from pathlib import Path
from typing import Optional, BinaryIO

import yaml
from yaml import FullLoader

from .uml_types import Config, ResourceStr, MissingSpritesConfig

BASE_PATH = os.path.dirname(os.path.realpath(__file__))


def load_config(path: str) -> Config:
    with open(path, 'r', encoding='utf8') as f:
        ret = yaml.load(f, FullLoader)
        if 'paths' in ret:
            ret['paths'] = [Path(os.path.expanduser(path)).resolve() for path in ret['paths']]
        return ret


def generate_localization(loc_key: str, loc_str: str, number: Optional[int] = None):
    return f" {loc_key}:{number if number is not None else ''} \"{loc_str}\""


def generate_resource_loc(resource: ResourceStr):
    if isinstance(resource, str):
        return f"£{resource}£ ${resource}$"
    else:
        if resource[1]:
            return resource[1]
        else:
            return f"£{resource[0]}£ ${resource[0]}$"


class Writer:
    def __init__(self, file: str, has_bom = True):
        self.file = file
        self._spacer = WriterSpacer(self)
        self.has_bom = has_bom

    def __enter__(self):
        self.io: BinaryIO = open(self.file, 'wb')
        if self.has_bom:
            self.io.write(codecs.BOM_UTF8)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.io.close()

    def write(self, s: str):
        self.io.write(s.encode("utf-8"))

    def write_language(self, lang_key: str):
        self.write(f"l_{lang_key}:\n")

    def write_localization(self, loc_key: str, loc_str: str, number: Optional[int] = None):
        self.write(generate_localization(loc_key, loc_str, number) + '\n')

    def write_comment(self, comment: str):
        self.write(f" # {comment}\n")

    def write_spacer(self):
        self.write('\n')

    def with_spacer(self):
        return self._spacer


class WriterSpacer:
    def __init__(self, writer: Writer):
        self.writer = writer

    def __enter__(self):
        self.writer.write_spacer()

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


def create_sprites_for_cleanup(writer: Writer, missing_sprites: MissingSpritesConfig):
    writer.write("spriteTypes = {\n")
    for error in missing_sprites['errors'].split('\n'):
        writer.write("	spriteType = {\n")
        mod_name = error.split("\"")[-2].split('/')[-1].split('.')[0]

        writer.write(f"		name = \"GFX_{mod_name}\"\n")
        writer.write(f"		texturefile = \"{missing_sprites['default']}\"\n")
        writer.write("	}\n\n")

    writer.write("}\n")
