# Nonprofit Space Finder

This is a web-based brokerage for sublet space for nonprofits.
The project is the brainchild of [Maryland Nonprofits](http://marylandnonprofits.org/).

## Getting started

Clone the project.

    git clone https://github.com/josephturnerjr/spacefinder.git

Change directory into the project:

    cd spacefinder

Create a new virtual environment:

    virtualenv env

Enter the virtual environment:

    source env/bin/activate

Install the Python requirements:

    pip install -r REQUIREMENTS

Create a config.py file with your configuration:

    cd spacefinder
    cp example.config.py config.py
    # Edit config.py with your favorite editor, e.g. vi
    # vi config.py
    # See your newly-copied config.py for information on what to change
    # Make sure to actually create the image directory you set
    cd ..

Create the database:

    make db

See if things work:
    
    # This should start a development server at 0.0.0.0:5000
    make debug

Nice! Should be good to go.

## But... what about production?

I personally use Nginx and uwsgi. If you are using these tools, you can
take a look at the `conf/` folder in this project for example
configuration files.
