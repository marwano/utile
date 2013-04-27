
import os.path
from utile import safe_import

BASE_DIR = os.path.dirname(__file__)

lxml = safe_import('lxml')
Crypto = safe_import('Crypto')
bunch = safe_import('bunch')
