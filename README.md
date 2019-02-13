# I2P CRAWLER

HTTP crawling tool for the I2P Darknet sites.

Although it was originally conceived to be used for the I2P anonymous network, 
this tool can also be used for crawling some others HTTP based web sites 
like those found in TOR, Freenet and/or the surface web. 

The crawler automatically extracts links to other i2p site thus getting an overall 
view of the i2p darknet inter-connections.

## How to install

#### Requirements

The crawler relies on the use of an adequate environment to run it. Mandatory elements
for that are:

- Linux **Unbuntu 16.04** and above (it can bee run in older version)
- **I2P router** (latest version)
- **Mysql 5.7**, though some other DBMS can be used like SQLite.
- **Python 2.7** environment

#### Installation steps
TODO

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
