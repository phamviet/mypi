### Development

Prepare

    cd /home/pi
    git clone git@github.com:phamviet/mypi.git
    cd mypi
    virtualenv venv
    . venv/bin/activate
    python setup.py install
    

Run as service

    sudo cp scripts/mypi-dev.service /lib/systemd/system/
    sudo systemctl enable mypi-dev
    sudo systemctl mypi-dev start

Single command

    FLASK_APP=mypi/core.py FLASK_DEBUG=1 flask run --host=0.0.0.0 --with-threads 
    
    
### Credits
* http://flask.pocoo.org/
* https://getmdl.io/