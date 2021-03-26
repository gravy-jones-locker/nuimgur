sudo apt-get -y update

sudo apt-get -y install build-essential
sudo apt-get -y install python3-dev python3-venv python3-pip
sudo apt-get -y install uwsgi uwsgi-plugin-python3
sudo apt-get -y install nginx

cd /working-directory

python3 -m venv venv
source venv/bin/activate

pip3 install --upgrade pip
pip3 install wheel
pip3 install uwsgi
pip3 install django
pip3 install psutil

mkdir logs
mkdir repo

cd repo
git clone https://github.com/gravy-jones-locker/nuimgur.git .

# !! edit for setup-specific ip details
sudo cp server/django /etc/nginx/sites-enabled/django

# !! edit for setup-specific directories
sudo cp server/django.init /etc/uwsgi/apps-enabled/django.ini

# !! edit for setup-specific directories
sudo mv _dirconfig.py dirconfig.py

# !! edit for setup-specific ip details
sudo mv nuimgur/_settings.py nuimgur/settings.py

sudo service nginx restart
sudo service uwsgi restart