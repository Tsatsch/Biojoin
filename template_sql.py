from collections import Counter


def fancy_print(sql_resp):
    fancy_resp = []
    print(sql_resp)
    for value in sql_resp:
        fancy_resp.append(value[0])
    return fancy_resp


def preprocess_string(user_input):
    """add '' if needed for string values to apply in sql query"""
    if "\'" not in user_input or '\"' in user_input:
        user_input = user_input.replace('\"', '')
        user_input = f'\'{user_input}\''
    return user_input


def get_gene_info(db_connection, gene_symbol):
    """ Given a gene symbol, find all gene
    information stored in the gene table"""
    cur = db_connection.cursor()
    gene_symbol = preprocess_string(gene_symbol)
    cur.execute(f'SELECT * FROM gene WHERE gene_symb = {gene_symbol};')
    res = [value for value in cur.fetchall()]
    return res


def get_genes_on_chromosome(db_connection, chromosome):
    """ Given a chromosome id, find all gene
    symbols located in the chromosome"""
    cur = db_connection.cursor()
    chromosome = preprocess_string(chromosome)
    cur.execute(f'SELECT gene_symb FROM gene WHERE gene_chr = {chromosome};')
    res = [value for value in cur.fetchall()]
    return res


def find_diseases(db_connection, snp_id):
    """Given a SNP ID, find all diseases
    associated with the SNP"""
    cur = db_connection.cursor()
    snp_id = preprocess_string(snp_id)
    cur.execute(f'SELECT omim_name FROM omim WHERE omim.gene_symb IN '
                f'(SELECT gene_symb FROM dbsnp WHERE snp_id = {snp_id});')
    res = [value for value in cur.fetchall()]
    return res


def find_snp(db_connection, disease_name):
    """Given a disease name, find all SNP IDs
    associated with the disease"""
    cur = db_connection.cursor()
    disease_name = preprocess_string(disease_name)
    cur.execute(f'SELECT snp_id FROM dbsnp WHERE dbsnp.gene_symb IN '
                f'(SELECT gene_symb FROM omim WHERE omim_name = {disease_name});')
    res = [value for value in cur.fetchall()]
    return res


def get_drugs(db_connection, disease_name):
    """Given a disease name, search for a drug that can heal it,
        we filter the answer with 10 best drugs accordint to their toxicity
        --> see toxicity table"""
    cur = db_connection.cursor()
    disease_name = preprocess_string(disease_name)
    cur.execute(f'SELECT disease_drug.drug_name, toxicity.tox FROM disease_drug '
                f'JOIN toxicity ON disease_drug.drug_id = toxicity.drug_id '
                f'WHERE disease_drug.disease_name = {disease_name};')
    answer = cur.fetchall()
    # decimal to float and tuple to dict
    res_dict = {}
    for value in answer:
        res_dict[value[0]] = float(value[1])

    # sort by values (by toxicity) descending
    res_dict = {k: v for k, v in sorted(res_dict.items(),
                                        key=lambda item: item[1], reverse=True)}

    first_5 = list(res_dict.items())[:5]
    if len(first_5) == 0:
        fancy_string = "Ops, no drugs found. We hope you will survive this!"
    else:
        fancy_string = "Use these drugs:\n"
        fancy_string += f'ToxVal | Drug Name\n'
        fancy_string += f'------------------\n'
        for (drug,tox) in first_5:
            # fancy_string += f'{k} with {v}% toxicity\n'
            fancy_string += f'{tox}  | {drug}\n'

    return fancy_string[:-1]


def get_diseases(db_connection, drug_name):
    """Given a drug name, print all disease that can be handled with it,
        we filter the answer with 10 most prevalence (infected people) diseases
        --> see prevalence table"""
    cur = db_connection.cursor()
    drug_name = preprocess_string(drug_name)
    cur.execute(f'SELECT disease_drug.disease_name, prevalence.prevalence FROM disease_drug '
                f'JOIN prevalence ON disease_drug.disease_id = prevalence.disease_id '
                f'WHERE disease_drug.drug_name = {drug_name};')
    answer = cur.fetchall()
    # decimal to float and tuple to dict
    res_dict = {}
    for value in answer:
        res_dict[value[0]] = float(value[1])

    # sort by values (by prevalence) descending
    res_dict = {k: v for k, v in sorted(res_dict.items(),
                                        key=lambda item: item[1], reverse=True)}

    first_5 = list(res_dict.items())[:5]

    if len(first_5) == 0:
        fancy_string = "Ops, no diseases found. Why this drug even exist?"
    else:
        fancy_string = "These disease can be treated:\n"
        fancy_string += f'Prevalence | Diseases\n'
        fancy_string += f'-----------------\n'
        for (dis,pre) in first_5:
            # fancy_string += f'{drug[0]} with {drug[1]}% toxicity\n'
            fancy_string += f'{pre}   | {dis}\n'

    return fancy_string[:-1]


def get_genes_from_drug(db_connection, drug_name):
    """Given a drug name, print all the genes that are affected"""
    cur = db_connection.cursor()
    drug_name = preprocess_string(drug_name)
    cur.execute(f'select G.gene_symb, G.popularity from gene G where G.gene_symb IN '
                f'(select D.gene_symb from disease D JOIN disease_drug DD  '
                f'ON D.id = DD.disease_id WHERE DD.drug_name = {drug_name});')
    answer = cur.fetchall()
    res_dict = {}
    for value in answer:
        res_dict[value[0]] = float(value[1])
    # decimal to float and tuple to dict
    res_dict = {k: v for k, v in sorted(res_dict.items(),
                                        key=lambda item: item[1], reverse=True)}

    first_10 = list(res_dict.items())[:10]

    if len(first_10) == 0:
        fancy_string = "Ops, no genes found. Why this drug even exist?"
    else:
        fancy_string = "These genes are affected:\n"
        fancy_string += f'Popularity | Gene Symbols\n'
        fancy_string += f'-----------------\n'
        for (gene,pop) in first_10:
            fancy_string += f'{pop}      | {gene}\n'

    return fancy_string[:-1]



def get_chr_from_drug(db_connection, drug_name):
    """Given a drug name, print the most common chromosomes that are affected"""
    cur = db_connection.cursor()
    drug_name = preprocess_string(drug_name)
    cur.execute(f'SELECT gene.gene_chr FROM gene WHERE gene.gene_symb IN '
                f'(SELECT disease.gene_symb from disease WHERE disease.id IN '
                f'(SELECT disease_drug.disease_id FROM disease_drug '
                f'WHERE disease_drug.drug_name = {drug_name}));')
    answer = [gene[0] for gene in cur.fetchall()]
    if len(answer) == 0:
        fancy_string = "Ops, no chromosomes were found. Why this drug even exist?"
    else:
        count = Counter(answer)
        count = count.most_common(3)
        fancy_string = "These chromosomes are most commonly affected:\n"
        for value in count:
            fancy_string += f'Chromosome {value[0]}: {value[1]} affected genes\n'

    return fancy_string[:-1]


def get_diseases_from_chr(db_connection, chr_nr):
    """ Given the chromosome number, find all the disease that
    are associated with genes based on that chromosome. Filter the
    output with 5 diseases with most prevalence"""
    cur = db_connection.cursor()
    chr_nr = preprocess_string(chr_nr)
    cur.execute(f'SELECT D.id, D.disease_name, R.prevalence FROM disease as D JOIN '
                f'(SELECT disease_id, prevalence FROM prevalence WHERE disease_id IN '
                f'(SELECT disease_id FROM disease JOIN gene ON disease.gene_symb = gene.gene_symb '
                f'WHERE gene.gene_chr = {chr_nr})) as R ON R.disease_id = D.id;')
    answer = cur.fetchall()

    res_dict = {}
    for value in answer:
        res_dict[value[1]] = int(value[2])

    # sort by values (by prevalence) descending
    res_dict = {k: v for k, v in sorted(res_dict.items(),
                                        key=lambda item: item[1], reverse=True)}
    
    first_5 = list(res_dict.items())[:5]

    if len(first_5) == 0:
        fancy_string = "Ops, no diseases found"
    else:
        fancy_string = f"These disease are assosiated with chromosome {chr_nr}:\n"
        fancy_string += f"------------------------------------------------\n"
        for disease in first_5:
            # fancy_string += f'{drug[0]} with {drug[1]}% toxicity\n'
            fancy_string += f'{disease[0]}\n'

    return fancy_string[:-1]


def stats_diseases_on_chr(db_connection):
    """ Statistics: Count number of diseases for each chromosome"""
    cur = db_connection.cursor()
    all_chromosomes = list(range(1, 23))
    all_chromosomes.append('X')

    stats = []
    for chromosome in all_chromosomes:
        chromosome = preprocess_string(str(chromosome))
        cur.execute(f'SELECT count(*) FROM disease JOIN gene ON '
                    f'disease.gene_symb = gene.gene_symb WHERE gene.gene_chr = {chromosome};')
        answer = cur.fetchall()
        stats.append(answer[0][0])

    fancy_string = 'Chromosome-Diseases stats:\n'
    for chromosome, counts in zip(all_chromosomes, stats):
        fancy_string += f'Chromosome {chromosome}: {counts}\n'
    return fancy_string[:-1]


##what is the drug that can heal the most diseases (most universal drug)

def add_values_in_dict(sample_dict, key, list_of_values):
    ''' Append multiple values to a key in 
        the given dictionary '''
    if key not in sample_dict:
        sample_dict[key] = list()
    sample_dict[key].extend(list_of_values)
    return sample_dict

def stats_universal_drug(db_connection):
    cur = db_connection.cursor()
    
   
    cur.execute(f'SELECT disease_drug.disease_name, disease_drug.drug_name FROM disease_drug;')
    answer = cur.fetchall()
    

    # decimal to float and tuple to dict
    res_dict = {}
    
    for value in answer:
        add_values_in_dict(res_dict, value[1], [value[0]])

    len_dict ={}
    

    for key in res_dict:
        len_dict[key] = len(res_dict[key])

    # sort by values (by prevalence) descending      
    

    len_dict = {k: v for k, v in sorted(len_dict.items(),
                                    key=lambda item: item[1], reverse=True)}

    first_10 = list(len_dict.items())[:10]

   
    fancy_string = f"The most universal drugs:\n"
    fancy_string += f'Num of Diseases it can treat | Drug name\n'
    fancy_string += f"----------------------------------------\n"
    for (topdrug,numdis) in first_10:
            fancy_string += f'{numdis} | {topdrug}\n'
        
    return fancy_string

   
    
