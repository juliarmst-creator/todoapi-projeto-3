
#!/usr/bin/env bash

# Interrompe o processo se algum comando falhar.
set -o errexit

# Instala as dependências.
pip install -r requirements.txt

# Reúne os arquivos estáticos.
python manage.py collectstatic --no-input

# Aplica as migrations ao banco de dados.
python manage.py migrate
