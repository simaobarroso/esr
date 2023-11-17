
su - core
export DISPLAY=:0.0

cd /home/core/Desktop/esr/tp2/videocastTest

source venv/bin/activate

cd src/

python3 main_client.py movie.mjpeg 10.0.2.20 5540 5541

