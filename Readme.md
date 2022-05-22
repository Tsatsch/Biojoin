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
     <li><a href="#prerequisites">Getting Started</a>
    <li><a href="#getting-started">Getting Started</a>
    </li>
    <li><a href="#data">Usage</a></li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#code">Code review</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>

## About The Project
This project is part of the course BiS332. The aim of this project is to develop an integrative bio-information inference system using various biological databases. A database is created a with data about SNP, genes, and disease information from primary bioinformatician databases. Namely, the databases are SNP, EntrezGene, and OMIM databases. In addition, we should implement software that works on top of the database and helps the user to operate the database content. In particular, the software should allow the user to perform basic database operations such as search, update, and deletion.

The project consists of two steps: 1. Data extraction and integration and 2. building a software to operate with the data. 


![Project Overview](./images/project-structure.png)

## Build with 
This section will list some major frameworks/libraries used
* [Python 3.8.13](https://www.python.org/)
* [psycopg2](https://www.psycopg.org/)
* [pandas](https://pandas.pydata.org/)
* More python native build-in modules and libraries are used e.g. json, io

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

## Data
Here are the primary sources that are ignored for this git repository because of licensing reasons. The data is freely available on the web. Here are the corresponding links:
The main websites are: http://ctdbase.org/downloads/, https://snap.stanford.edu/biodata/datasets/10004/10004-DCh-Miner.html and data provided by the TA's for the course BiS332.
- [CTD_chemicals.xml](http://ctdbase.org/reports/CTD_chemicals.xml.gz)
- [CTD_diseases.xml](http://ctdbase.org/reports/CTD_diseases.xml.gz)
- [DCh-Miner_miner-disease-chemical.tsv](https://snap.stanford.edu/biodata/datasets/10004/10004-DCh-Miner.html)
- disease_OMIM.txt, gene_OMIM.txt, SNP.txt and Homo_sapiens_gene_info.txt were provided by TA's
- merged.txt is self constructed using disease_OMIM.txt and gene_OMIM.txt 

## Usage
### Stage 1: Data extraction and integration
Raw data was already provided by the course TAs and can be found in the data/ folder. Only the file merged.txt is generated in the script. 
Insertion of data from txt file into the PostgreSQL database tables.

Make sure you have the data/ folder with disease_OMIM.txt, gene_OMIM.txt, Homo_sapiens_gene_info.txt and SNP.txt files. Furthermore, fill the config.json file to establish the connection to the database.
```bash
python fill.py
```

### Stage 2: Operate with the data
The main file is the cmdline.py. It will launch a command-line interface with that user can search, update and delete entries in the database that is provided in the config.json file. 
```bash
python cmdline.py
```
![Command-line interface](./images/cmdline.png)

## Technical Details

### Database architecture (DDL)
For more information check the ddl.sql file. 
```sql
CREATE TABLE dbSNP (
  snp_id int NOT NULL,
  snp_chr varchar,
  snp_pos varchar,
  gene_symb varchar,
  anc_allele varchar,
  min_allele varchar,
  PRIMARY KEY (snp_id)
);

CREATE TABLE Gene (
  tax_id varchar,
  gene_id int UNIQUE,
  gene_symb varchar NOT NULL,
  gene_syn varchar,
  gene_chr varchar,
  gene_pos varchar,
  gene_sum text,
  gene_type varchar,
  gene_mod_date date NOT NULL,
  PRIMARY KEY (gene_id)
);


CREATE TABLE OMIM (
  omim_id int,
  omim_name varchar,  
  gene_symb varchar,
  PRIMARY KEY (omim_id, gene_symb)
  );
```
### Database insertion
The database tables have to be created manually using the above-provided SQL statements. This step is a prerequisite for using the software to operate the database. 

The python script fill.py connects to the database using the configuration data such as database username, password, host, and name from the config.json file. After a preprocessing step, the data from the tables is inserted into the database tables (the tables should have already been created in the database manually). An essential step in the preprocessing is merging the two files gene_OMIM.txt and disease_OMIM.txt with an outer join method. This step is crucial since we have a relational table in our database with attributes omim_id int, omim_name, and gene_symb. The join result tsv file is merged.txt, which is then directly used to insert the data into the omim table.  

Data is preprocessed to a format that is the most convenient to insert data with. A dictionary is generated from the txt files to make a object csv and copy into db for best performance. The idea is obtained from copy_stringio() in https://hakibenita.com/fast-load-data-python-postgresql.

In the end, Homo_sapiens_gene_info.txt was inserted into the Gene table, SNP.txt into dbSNP and merged.txt into the OMIM table of our database.

![Database](./images/database.png)

### Database operation
#### Structure of the program:
- cmdline.py initializes and ends the program
- based on user input a pre_{search/update/delete} function is started to obtain more data from teh user in order to pass it as arguments for the search/update/delete function.
- search/update/delete function construct a SQL query and parse the output from the database
- template_sql.py gives some basic function user can try to test the database (the queries are part of the project exercise)

## Extra features
- for update/adding new row the program automatically distinguish if the datatype of column is string or integer and corrects the user input to the right format
- suggested tables and columns are obtained from the database everytime the program is launched, it means it is not hard-coded and is always up-to-date
