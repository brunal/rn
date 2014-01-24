Installation
============
Dépendances externes : python2, sqlite3

Dans un shell, pour installer les bibliothèques requises, faire

`pip install -r requirements.txt`

Il faut ensuite écrire le fichier `config.yml` en s'inspirant de `config.yml.example`.


Enfin, créer la base de données. Pour cela, dans l'interpréteur Python,

```python
from tools import db
db.create_all()
```

Lancement
=========

`./main.py`
