# Weather data analyzer

#### Introduction
Weather data analyzer is a python program which reads weather data from .csv files and perform analysis on temperature and wind speed and show/visualize results without any third party module.

#### Data Source
Data is taken from the following source: https://geographic.org/global_weather/index.html

You can view data for any country/city from given source. In this repository, data of first three months of 2016 of Cork is being used. (Cork is city in Ireland)

#### Structure
The repository consists of **data** folder and **main.py** file.

**data** folder contains weather data in the form of **csv**

**main.py** is a code file which analyze and show/visualize results.
 
#### Usage
Run **main.py** file with the following command line arguments:

**path:** Weather files directory path containing .csv files. 

**-e:** To see highest temperature and day, lowest temperature and day, fastest wind speed and day, and slowest mean wind speed and day of the year. **Usage:** -e yyyy

**-s:** To see one line horizontal bar charts on the console for the highest and lowest temperature on each day of given month of year. **Usage:** -s yyyy/mm

**-c:** To see two line horizontal bar charts on the console for the highest and lowest temperature on each day of the given month of year. **Usage:** -c yyyy/mm  

#### Examples

python main.py PATH_HERE -e 2016

python main.py PATH_HERE -s 2016/03

python main.py PATH_HERE -c 2016/03

