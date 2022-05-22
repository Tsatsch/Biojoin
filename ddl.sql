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


-- CREATE TABLE OMIM (
--  omim_id int,
--  omim_name varchar,
--  gene_symb varchar,
--  PRIMARY KEY (omim_id, gene_symb)
--  );



-- CREATE TABLE DISEASE (
--     disease_name varchar,
--     id varchar,
--     alt_id varchar,
--     PRIMARY KEY (id)
-- );

CREATE TABLE Disease (
    disease_name varchar,
    id varchar,
    alt_id varchar,
    gene_symb varchar,
    PRIMARY KEY (id, gene_symb)
);

CREATE TABLE Disease_Drug (
    drug_name varchar ,
    drug_id varchar,
    disease_name varchar,
    disease_id varchar,
    PRIMARY KEY (drug_id, disease_id)
 );