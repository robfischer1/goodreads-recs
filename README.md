## WreckSys
WreckSys is a sequential recommendation system for Fantasy & Paranormal novels built in TensorFlow. Originally designed to deliver terrible recommendations on purpose, it now does so mostly by accident.

Recommendations are based on the [Goodreads Dataset](https://mengtingwan.github.io/data/goodreads)

It was originally as a [WGU](http://www.wgu.edu/) Capstone project before taking on a life of its own.

### About

See it in action at [https://www.wrecksys.com/](https://www.wrecksys.com/)  
See how it was built on [Google Colab](#)

### Usage

Wrecksys is compatible with both Linux and Windows.  
Installing on WSL is preferred on Windows to allow access to tensorflow-gpu.

Wrecksys relies on a very large dataset. The fastest way to get up and running is via Google Colab:

```jupyter
%%bash
git clone https://github.com/robfischer1/wrecksys wrecksys && cd wrecksys
pip install -r requirements.txt
```

Alternatives include:  
*environment.yml* if you would prefer to experiment in [Conda](https://repo.anaconda.com/miniconda/Miniconda3-latest-Windows-x86_64.exe)  
*requirements.txt* to install in the virtual environment of your choice.

### License

[BSD-3-Clause-Clear](https://choosealicense.com/licenses/bsd-3-clause-clear/)