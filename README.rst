Sharding Simulator
==================

This is a Sharding Simulator to study blockchain scalability.

How to run on Ubuntu
====================

First make sure you have the header file for Python.

$ sudo apt install python3-dev

Then, install MPI (openmpi in this case).

$ sudo apt install libblacs-mpi-dev

Then, install virtualenv if you don't have it yet.

$ sudo apt install virtualenv

Create a virtual environment with python3.6.

$ virtualenv  --no-site-packages -p python3.6 venv

Activate the virtual environment.

$ source venv/bin/activate

Install the python packages required.

$ pip install -r requirements.txt

Add you prefered browser in self.browser in configuration.py

$ vi shardSim/configuration.py

You are ready to run!

$ make

Enjoy!!! :)
