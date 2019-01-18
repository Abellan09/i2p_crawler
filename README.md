# I2P CRAWLER

This tool enables crawling on the I2P Darknet.

## How to install

You can launch the crawler on Windows 10 and Ubuntu Linux (from 16.04 version) systems.

In both systems, just download or clone this repository:

```
git clone https://github.com/Abellan09/i2p_crawler
```

Then, you have to install/configure some things:

First of all, it is neccesary to install an instance of I2P.
In second place, you need Python 2.7 and Scrapy.
It is recommended to install DB Browser for SQLite to manage the database easily.
Last, you have to create the "ongoing" and "finished" directories.

### Windows

1) I2P.

Download (and execute) the installer from [I2P](https://geti2p.net/es/download).

2) Python and Scrapy

Download (and execute) the installer from [Python](https://www.python.org/downloads).
Then, to install scrapy: ```pip install scrapy```

3) DB Browser for SQLite.

Download (and execute) the installer from [SQLite Browser](https://sqlitebrowser.org).

4) Ongoing and finished directories.

Go to the root of the cloned project.
Change directory to ~/spiders and create the directories inside it.

```
cd /i2p_crawler/crawler/i2p/i2p/spiders
mkdir ongoing
mkdir finished
```

### Linux

1) I2P.

```
sudo apt-add-repository ppa:i2p-maintainers/i2p
sudo apt-get update
sudo apt-get install i2p
```

2) Python and Scrapy

```
sudo apt install python2.7
sudo apt install python-pip
sudo pip install scrapy
```

3) DB Browser for SQLite.

```
sudo add-apt-repository -y ppa:linuxgndu/sqlitebrowser
sudo apt-get update
sudo apt-get install sqlitebrowser
```

4) Ongoing and finished directories.

```
cd /i2p_crawler/crawler/i2p/i2p/spiders
mkdir ongoing
mkdir finished
```

## Usage example

First, you have to raise an instance of I2P (it is recommended that the instance is active as much time as possible for better results).

In Windows, just click on the "Start I2P" button; in Linux, start the service with ```i2prouter start```

Then, go to the directory ~i2p_crawler/crawler/i2p with ```cd ~/i2p_crawler/crawler/i2p/``` and run the crawler:

```
python manager.py
```

The script "manager.py" will try to crawl the entire I2P (all the eepsites it finds). This can take too much time (difficult to estimate).
If you prefer crawling only one eepsite, run the spider "spider.py" in the next way:

```
scrapy crawl i2p -a url=URL -o OUTPUT.json
```

Where "URL" is the URL of the eepsite you want to crawl and "OUTPUT" is the name of the file where the results of crawling will be.
For example:

```
scrapy crawl i2p -a url=http://eepsite.example.i2p -o output_example.json
```

## Built With

* [Python](https://www.python.org) - Used language.
* [Scrapy](https://scrapy.org) - Used crawling framework.

## Authors

* **Alberto Abellán**
* **Roberto Magán**
* **Gabriel Maciá-Fernández**

See also the list of [contributors](https://github.com/Abellan09/i2p_crawler/graphs/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
