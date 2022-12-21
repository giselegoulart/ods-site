# ODS-Mapeados-django

O app accounts serviria para gerenciar o cadastro e login dos usuários, caso isso não venha a ser implementado, é possível apenas excluir o app.

O app home serve para distribuir as páginas estáticas, como 'index.html' e 'sobre-os-ODS.html'.

# Instalando o projeto

Para instalar o projeto, faça o clone, e em seguida (dentro de um ambiente virtual, caso prefira),  com o terminal na pasta que contém o projeto (essa é a pasta que contém os arquivos 'manage.py' e 'requirements.txt'), rode o comando `pip install -r requirements.txt`; isso irá instalar as dependências do projeto.
Em seguida, execute o comando `python manage.py migrate`.

# Rodando o site

Para rodar o site em um servidor de desenvolvimento, com o terminal na pasta que contém o projeto (essa é a pasta que contém os arquivos 'manage.py' e 'requirements.txt'), execute o comando `python manage.py runserver`. 
Isso irá imprimir no terminal a URL do site neste servidor de desenvolvimento na sua máquina, basta seguir a URL para utilizá-lo.

# Celery e tasks assíncronas periodicas

O projeto conta com celery e celery beat configurados; mais especificamente, existem duas tasks: uma que é rodada a cada 1h para limpar a pasta /media/, na qual os conteúdos do processamento de arquivos ficam guardados, e outra que é rodada a cada 24h para limpar as sessions expiradas da tabela django_sessions em db.sqlite3, que armazena as sessões criadas pelo SessionMiddleware.

Para rodar o celery com essas tasks assíncronas, primeiro inicie um worker em um terminal separado com o seguinte comando:

    $ celery -A ODSMAP.celery worker --loglevel=info

Em seguida, em outro terminal, inicie o scheduler celery beat com o seguinte comando:

    $ celery -A ODSMAP.celery beat --loglevel=info

Caso esteja utilizando Windows, os comandos são, respectivamente:

    > celery -A ODSMAP.celery worker -P gevent --loglevel=info

e

    > celery -A ODSMAP.celery beat --loglevel=info

Isso fará com que o scheduler agende a task de limpeza de arquivos temporários a cada 1h e a task de limpeza de sessões expiradas a cada dia (24h), além de fazer com que o worker iniciado as realize.
