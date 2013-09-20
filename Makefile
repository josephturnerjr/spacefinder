PYTHON = ./env/bin/python

run: 
	tmux new-session -d -s olgn '$(PYTHON) runserver.py'
	tmux splitw -h -t olgn 'cd spacefinder/static/css; ~/bin/lesswatch'
	tmux attach

debug:
	$(PYTHON) runserver.py

db:
	$(PYTHON) create_db.py

test:
	$(PYTHON) -m unittest discover tests/

dummy:

.PHONY: env dummy
