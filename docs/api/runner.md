# Runner

::: starvellapi.Runner
    options:
      show_bases: true
      members_order: source

## State store

`Runner` принимает опциональный `state_store` со следующим интерфейсом:

```python
from typing import Any, Protocol

class StateStore(Protocol):
    def get(self, key: str, default: Any = None) -> Any: ...
    def set(self, key: str, value: Any) -> None: ...
```

Любой объект с такими методами подойдёт. Минимальная реализация на JSON-файле:

```python
import json
from pathlib import Path

class JsonStateStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._data = {}
        if self.path.exists():
            self._data = json.loads(self.path.read_text(encoding="utf-8"))

    def get(self, key, default=None):
        return self._data.get(key, default)

    def set(self, key, value):
        self._data[key] = value
        self.path.write_text(json.dumps(self._data, ensure_ascii=False), encoding="utf-8")
```

С таким store `Runner` переживает рестарты и не выдаёт всю историю как «новые» события.
