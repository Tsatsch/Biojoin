# Biojoin Project 
Course: KAIST Spring 2022, Bio-Information Processing (BiS332) by Prof. Doheon Lee

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
     <li><a href="#prerequisites">Prerequisites</a>
    <li><a href="#getting-started">Getting Started</a>
    </li>
  </ol>
</details>

## About The Project
This project is part of the course BiS332. The aim of this project is to develop an integrative bio-information inference system using various biological databases. A database is created a with data about SNP, genes, and disease information from primary bioinformatician databases. Namely, the databases are SNP, EntrezGene, and OMIM databases. In addition, we should implement software that works on top of the database and helps the user to operate the database content. In particular, the software should allow the user to perform basic database operations such as search, update, and deletion. For the last phase of the project we established a database system that deals with Disease-Drug relations and accommodates data from external sources. An organized disease-drug database system is mandatory to help physicians catch up with the current trends in bio-pharmaceutical practice.
With this, we introduced the ‘scoring’ system, which may be implemented to suggest the best drug, disease, or other components for a particular system, in which several factors can refer to this ‘scoring’.

The project consists of two steps: 1. Data extraction and integration and 2. building a software to operate with the data. 


![Project Overview](./images/project-structure.png)

## Build with 
This section will list some major frameworks/libraries used
* [Python 3.8.13](https://www.python.org/)
* [psycopg2](https://www.psycopg.org/)
* [pandas](https://pandas.pydata.org/)
* [progressbar](https://pypi.org/project/progressbar2/) (optional)  
* More python native build-in modules and libraries are used e.g. json, io, Counter, 

## Prerequisites
- postgres database you can access with known credentials

## Getting Started
1. Python installation
   - in case you want different specific python versions and separate isolated environments, I recommend you yo use conda (https://docs.conda.io/en/latest/) 
   - otherwise you can downlaod python with homebrew for Mac or on the official website https://www.python.org/downloads/
2. Repository clone
   - clone this repository by forking it 
3. psycopg2 and pandas
   - install both Python packages with pip one by one
   - alternatively use the requirements.txt file to install all packages at once
```bash
pip install -r /path/to/requirements.txt
```
4. config.json file
   - for the config file you need:
     - host name (db_host)
     - database name (db_name)
     - username for the database (db_user)
     - password for the database (db_pw)
   - port is default = 5432 
