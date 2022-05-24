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
        for drug in first_5:
            # fancy_string += f'{drug[0]} with {drug[1]}% toxicity\n'
            fancy_string += f'{drug[0]}\n'

    return fancy_string


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
        for disease in first_5:
            # fancy_string += f'{drug[0]} with {drug[1]}% toxicity\n'
            fancy_string += f'{disease[0]}\n'

    return fancy_string


def get_genes_from_drug(db_connection, drug_name):
    """Given a drug name, print all the genes that are affected"""
    cur = db_connection.cursor()
    drug_name = preprocess_string(drug_name)
    cur.execute(f'SELECT disease.gene_symb from disease WHERE disease.id IN '
                f'(SELECT disease_drug.disease_id FROM  '
                f'disease_drug JOIN prevalence ON disease_drug.disease_id = prevalence.disease_id '
                f'WHERE disease_drug.drug_name = {drug_name});')
    answer = [gene[0] for gene in cur.fetchall()]
    # decimal to float and tuple to dict
    clean_answer = []
    for value in answer:
        if value != "None":
            clean_answer.append(value)

    clean_answer = sorted(clean_answer)
    if len(clean_answer) == 0:
        fancy_string = "Ops, no genes found. Why this drug even exist?"
    else:
        fancy_string = "These genes are affected:\n"
        for gene in clean_answer:
            # fancy_string += f'{drug[0]} with {drug[1]}% toxicity\n'
            fancy_string += f'{gene}, '

    return fancy_string[:-2]


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

    return fancy_string
