import fill


def fancy_print(sql_resp):
    fancy_resp = []
    for value in sql_resp:
        fancy_resp.append(value[0])
    return fancy_resp


def get_gene_info(db_connection, gene_symbol):
    """ Given a gene symbol, find all gene
    information stored in the gene table"""
    cur = db_connection.cursor()
    cur.execute(f'SELECT * FROM gene WHERE gene_symb = \'{gene_symbol}\';')
    res = [value for value in cur.fetchall()]
    cur.close()
    db_connection.close()
    return res


def get_genes_on_chromosome(db_connection, chromosome):
    """ Given a chromosome id, find all gene
    symbols located in the chromosome"""
    cur = db_connection.cursor()
    cur.execute(f'SELECT gene_symb FROM gene WHERE gene_chr = \'{chromosome}\';')
    res = [value for value in cur.fetchall()]
    cur.close()
    db_connection.close()
    return res


def find_diseases(db_connection, snp_id):
    """Given a SNP ID, find all diseases
    associated with the SNP"""
    cur = db_connection.cursor()

    cur.execute(f'SELECT omim_name FROM omim WHERE omim.gene_symb IN '
                f'(SELECT gene_symb FROM dbsnp WHERE snp_id = {snp_id});')
    res = [value for value in cur.fetchall()]
    cur.close()
    db_connection.close()
    return res


def find_snp(db_connection, disease_name):
    """Given a disease name, find all SNP IDs
    associated with the disease"""
    cur = db_connection.cursor()

    cur.execute(f'SELECT snp_id FROM dbsnp WHERE dbsnp.gene_symb IN '
                f'(SELECT gene_symb FROM omim WHERE omim_name = \'{disease_name}\');')
    res = [value for value in cur.fetchall()]
    cur.close()
    db_connection.close()
    return res


# example usage
conn = fill.connect_db('config.json')
result = get_gene_info(conn, 'NAT2')
print(result)
result = get_genes_on_chromosome(conn, '2')
print(result)
result = find_diseases(conn, 1289671)
print(result)
result = find_snp(conn, 'Bamforth-Lazarus syndrome')
result = fancy_print(result)
print(result)