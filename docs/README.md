# AOS IBA Probe Tutorials

This directory contains a series of AOS IBA probe tutorials using the aospy.ibaproblib package.
These tutuorials are designed to operate using the Jupyter notebook environment.

# Setup

## Jupyter Notebook

To install Jupyter notebook in your enviornment, we first recommend that you create and activate a 
python virtual environment.  Please use Python 2 at this time.  Once you have activated
your virtual environment, run the following commands to install Jupyter notebook:


```bash
(venv)$ pip install ipython==5 jupyter
```

## AOS IBA probe library

This repository contains an example probe library that you can install into your 
virtual environment.  Go to the top of this repository where you find the `setup.py`
file and run the following command:

```bash
(venv)$ python setup.py develop
```

This will install the aospy.ibaprobelib into your environemnt so that you can also make changes
and experiement with the code if you like.

## AOS Python Swagger Client

Finally install the AOSpy API client.  This library allows you to interact with the AOS
REST API making use of the Swagger 2.0 API definitions provided from the AOS server.  To
install this package, run the following command:

```bash
(venv)$ pip install apstra-aospy-swagger
```

# Running the Tutorials

Once you have completed the above setup, you can launch the Jupyter notebook environment
on your laptop.  Ensure that you are in the directory with the notebook files (*.ipynb),
and run the following command:

```bash
(venv)$ jupyter notebook
```

This command will launch a web-browers with a directory tree showing all of the files.
Click on one of the tutorials you want to try out.

For more information on using Jupyter notebooks, please refer to the online documentation. 
The beginners guide is located [here](https://jupyter-notebook-beginner-guide.readthedocs.io/en/latest/).