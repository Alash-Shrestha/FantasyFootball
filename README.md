# Fantasy League

## Getting Started

Setup project environment with [virtualenv](https://virtualenv.pypa.io) and [pip](https://pip.pypa.io).

### Linux
```bash
$ virtualenv project-env
$ source project-env/bin/activate
$ pip install -r requirements.txt
$ python manage.py migrate
$ python manage.py runserver
```

### Windows
```bash
$ python -m venv project-env
$ .\project-env\Scripts\activate
$ pip install -r requirements.txt
$ python manage.py migrate
$ python manage.py runserver
```



## Admin User

* First set up and superuser account where the user can maintain the system 
```bash
$ python manage.py create superuser
```
enter the credentials you want to set up and then , user credentials to login to 
http://localhost:8000/admin

* Go to the url http://localhost:8000/admin/fantasy/matchpointmapper/ and check if the mapper is set or not. if the mapper is not set set the points to be distributed for each goal and assist of a player. 
* Go to the url http://localhost:8000/admin/fantasy/matchweek/ and set up the current match week for which the game scores and points if to be determined. 
* Add teams and players from this urls:
* http://localhost:8000/admin/fantasy/player/
* http://localhost:8000/admin/fantasy/team/
* After that you can set up match for that particulary match week: http://localhost:8000/admin/fantasy/match/ For each match select scores, teams and scorers and the players with assists. Once it is done , you are ready to sync match points.
* After this, on top corner. on navbar, there is a nav item "sync points". click on it, it should take you to the new page, and give you status of match week sync points. It calculates the matchweek points for current active week. Current active week is the latest week for which is_sync status is False. 
* After this, you should see changes in your fantasy teams users dashboard.

