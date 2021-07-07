## WIP

Ative o ambiente virtual:
```bash
pipenv shell
```

Comando para rodar os testes:
```bash
coverage run --source . manage.py test -v 2 | grep test*
coverage report -m
```