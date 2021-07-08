## WIP

Ative o ambiente virtual:
```bash
pipenv shell
```

Instale as biblicas:
```bash
pipenv install
```

Comando para rodar os testes:
```bash
coverage run --source . manage.py test
coverage report -m
```

Rode as migrações:
```bash
python3 manage.py makemigrations
python3 manage.py migrate
```

Inicie a aplicação:
```bash
python3 manage.py runserver
```