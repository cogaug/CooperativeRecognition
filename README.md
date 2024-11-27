# Recognition Expansion
**writing..**

**prerequisite**

 - Anaconda

 - python3.10

**Installtion**
```
# install CARLA
# CARLA version == 0.9.15

$ mkdir carla
$ cd mkdir

#download carla 0.9.15
$ wget https://tiny.carla.org/carla-0-9-15-linux
$ tar -xvzf CARLA_0.9.15.tar.gz
$ sudo apt-get install libomp5

#download carla 0.9.15 additional Maps
$ cd Import
$ wget https://tiny.carla.org/additional-maps-0-9-15-linux

Import the additional maps
$ ./ImportAssets.sh

#check the carla
./CarlaUE4.sh

#install python modules
$ pip install carla
$ pip install install --user pygame numpy
$ pip install cv2

# modify the bashrc
$ gedit ~/.bashrc

export CARLA_ROOT=/home/{user}/carla
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.13-py3.7-linux-x86_64.egg:$CARLA_ROOT/PythonAPI/carla

$ source ~/.bashrc

```

**Running**
```
$ python run.py
```
