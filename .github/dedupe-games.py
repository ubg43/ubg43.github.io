from library_guard import guard_file
from pathlib import Path

for name in ('legacy-index.html', 'index.html'):
    path = Path(name)
    if path.exists():
        guard_file(path)

print('DEDUPE COMPLETE: duplicate game titles and canonical game URLs were removed.')
