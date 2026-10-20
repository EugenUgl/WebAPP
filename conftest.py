import sys
from pathlib import Path

# Добавляем корень проекта в sys.path, чтобы тесты могли импортировать
# пакеты сервисов (например, gateway.gateway), запускаясь из любой директории.
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
