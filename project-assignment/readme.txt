Sep intra system is composed of the react frontend (newadmin) and the django backend (django-workflow-backend).

To install the dependencies for the front end (newadmin)

cd newadmin

npm install --legacy-peer-deps

npm run dev

Then you can access the localhost:5371 at the browser.

To install the dependencies for the back end (django-workflow-backend).

You need to have uv, which is a package manager like conda for python or npm for node.

Following is the command for installing uv

powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

Then restart the terminal/powershell/cmd,

cd django-workflow-backend

uv sync

Then you need to load the database (Following command will generate a database and load some data into it)

uv run python manage.py migrate
uv run python manage.py loaduser
uv run python manage.py loadeventrequest
uv run python manage.py loadtask

Finally, everything is prepared and you are ready to start the server.

uv run python manage.py runserver

Additionally, to run the test:

uv run python manage.py test

You can also execute test from one workflow only:

uv run python manage.py test apps.users