Installation
============
Dépendance : python2, sqlite3

Dans un shell,

`pip install -r requirements.txt`

Il faut ensuite écrire le fichier `config.yml` en s'inspirant de `config.yml.example`.


Enfin, créer la base de données. Pour cela, dans l'interpréteur Python,

```python
from app import create_app
from models import db
app = create_app()
app.test_request_context().push()
db.create_all()
```

Lancement
=========

`./main.py`
