run: 
	tmux new-session -d -s olgn './env/bin/python runserver.py'
	tmux splitw -h -t olgn 'cd spacefinder/static/css; ~/bin/lesswatch'
	tmux attach

debug:
	python runserver.py

db:
	python create_db.py

test:
	python -m unittest discover tests/

dummy:

.PHONY: env dummy
