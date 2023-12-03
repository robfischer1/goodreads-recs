## WreckSys
WreckSys is a sequential recommendation system for Fantasy & Paranormal novels built in TensorFlow. Originally designed to deliver terrible recommendations on purpose, it now does so mostly by accident.

Recommendations are based on the [Goodreads Dataset](https://mengtingwan.github.io/data/goodreads)

It was originally created as a [WGU](http://www.wgu.edu/) Capstone project before taking on a life of its own.

### About
[https://www.wrecksys.com/](https://www.wrecksys.com/)

The current implementation and all associated documents are also available on the project [website](https://www.wrecksys.com/).

### Installation

Wrecksys is compatible with both Linux and Windows. Installing on WSL is preferred on Windows to allow access to tensorflow-gpu.

The fastest way to get up and running is to install [Conda](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe), clone the repository, and run *start.py* from the Anaconda Prompt.

Requirements and dependencies are listed in environment.yml at the root of the repository if you would prefer to install manually. 

```bash
git clone https://github.com/robfischer1/capstone wrecksys
cd wrecksys
python -m start.py
```

### Docker
The project frontend can be found in src/wrecksys_one


### License

[BSD-3-Clause-Clear](https://choosealicense.com/licenses/bsd-3-clause-clear/)