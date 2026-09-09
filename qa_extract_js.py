from pathlib import Path
import re

html = Path('index.html').read_text(encoding='utf-8')
blocks = re.findall(r'<script>(.*?)</script>', html, flags=re.S)
if len(blocks) != 1:
    raise SystemExit(f'EXPECTED_ONE_INLINE_SCRIPT_GOT_{len(blocks)}')
Path('/tmp/xiaoxianji-inline.js').write_text(blocks[0], encoding='utf-8')
print('EXTRACTED', len(blocks[0]), 'bytes')
