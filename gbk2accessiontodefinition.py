#!/usr/bin/python

import argparse
from Bio import SeqIO
import re
import parse_newick_tree
from Bio import Phylo


def get_coressp(gbk_file_list, molis_table):
    name2description = {}
    for file in gbk_file_list:
        records = [i for i in SeqIO.parse(file, "genbank")]

        name = records[0].name
        description = records[0].description
        description = re.sub(" DNA, complete genome\.", "", description)
        description = re.sub(", complete genome\.", "", description)
        description = re.sub(", complete genome", "", description)
        description = re.sub(", complete sequence\.", "", description)
        description = re.sub("strain ", "", description)
        description = re.sub("str\. ", "", description)
        description = re.sub(" complete genome sequence\.", "", description)
        description = re.sub(" complete genome\.", "", description)
        description = re.sub(" chromosome", "", description)
        description = re.sub(" DNA", "S.", description)
        description = re.sub("Merged record from ", "", description)
        description = re.sub(", wgs", "", description)
        description = re.sub("Candidatus ", "", description)
        description = re.sub(".contig.0_1, whole genome shotgun sequence.", "", description)
        description = re.sub("Staphylococcus", "S.", description)
        description = re.sub(" complete genome", "S.", description)
        description = re.sub(" plasmid", "", description)
        description = re.sub("plasmid", "", description)
        description = re.sub(" subsp. aureus", "", description)

        #description = re.sub("aureus aureus", "aureus", description)


        name2description[name] = description


    with open(molis_table) as f:
        for line in f:
            line = line.rstrip().split('\t')
            name2description[line[3]] = line[1]



    return name2description


if __name__ == '__main__':
    import argparse
    from Bio import SeqIO
    import re
    import parse_newick_tree
    from Bio import Phylo
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", '--input_gbk', type=str, help="input gbk files", nargs='+')
    parser.add_argument("-m", '--molis_table', type=str, help="input molis number table")
    parser.add_argument("-t", '--tree', type=str, help="input tree")

    args = parser.parse_args()
    id2description = get_coressp(args.input_gbk, args.molis_table)
    new_tree = parse_newick_tree.convert_terminal_node_names(args.tree, id2description)
    print "writing converted tree..."

    with open("parsnp_renames.nwk",'w') as output_tree:
        Phylo.write(new_tree, output_tree, 'newick')