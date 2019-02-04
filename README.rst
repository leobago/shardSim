Sharding Simulator
==================

This is a Sharding Simulator to study blockchain scalability.

How to run on Ubuntu
====================

First make sure you have the header file for Python.

.. code-block:: shell

  sudo apt install python3-dev

Then, install MPI (openmpi in this case).

.. code-block:: shell

  sudo apt install libblacs-mpi-dev

Then, install virtualenv if you don't have it yet.

.. code-block:: shell

  sudo apt install virtualenv

Create a virtual environment with python3.6.

.. code-block:: shell

  virtualenv  --no-site-packages -p python3.6 venv

Activate the virtual environment.

.. code-block:: shell

  source venv/bin/activate

Install the python packages required.

.. code-block:: shell

  pip install -r requirements.txt

You are ready to run!

.. code-block:: shell

  make

Enjoy!!! :)

