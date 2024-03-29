#!/usr/bin/env python
# python 2.7.5 requires biopython

########### promer2circos ############

def get_contig(location, contig_coordlist, contig_pos):
    # print 'location', location
    # print contig_coordlist
    for i, one_contig in enumerate(contig_coordlist):
        if location >= one_contig[1] and location <= one_contig[2]:
            # print 'match!'
            return one_contig, contig_coordlist[i + 1:len(contig_coordlist)], location
        elif location > contig_coordlist[i - 1][2] and location <= one_contig[1]:
            # print 'between contigs!'
            if contig_pos == 'start':
                # print "start located between contigs,------", location, '-->new start:', one_contig[1]
                # print one_contig
                # print contig_coordlist[i+1:len(contig_coordlist)]
                # return contig start as location
                return one_contig, contig_coordlist[i + 1:len(contig_coordlist)], one_contig[1]
            else:
                # print "end located between contigs-------", location, '-->new end:', contig_coordlist[i-1][2]
                # end of contig located between contigs, return previous contig data
                # print 'contig', contig_coordlist[i-1]
                # print 'following contigs', contig_coordlist[i:len(contig_coordlist)]
                return contig_coordlist[i - 1], contig_coordlist[i:len(contig_coordlist)], contig_coordlist[i - 1][2]

        else:
            # print "partial match, probably overlap between end contig and gap region", one_contig
            continue
    return False, False, False


def rename_karyotype(contig_coords, data_list):
    '''

    :param contig_coords: chr - NZ_JSAM00000000_1 NZ_JSAM00000000_1 0 104228 spectral-5-div-4 ==> keep 3, 4 et 5
    :param data_list: list of contig coords: [[contig_X, start, end],[...]]
    :return:
    '''

    import copy

    renamed_data = []
    for i, data in enumerate(data_list):
        start = int(data[1])
        end = int(data[2])
        # print i, data
        contig_start, following_contigs1, position1 = get_contig(start, contig_coords, contig_pos="start")

        contig_end, following_contigs2, position2 = get_contig(end, contig_coords, contig_pos="end")

        if (contig_start is False) or (contig_end is False):
            # print 'one falese!'
            # print start, end, contig_start, contig_end

            if start > contig_coords[-1][1]:
                # print 'last contig'
                contig_start, following_contigs1, position1 = contig_coords[-1], [], start
                contig_end, following_contigs2, position2 = contig_coords[-1], [], contig_coords[-1][2]
        if contig_end is False:
            continue
        # print 'contig_start', contig_start
        # print 'contig_end', contig_end
        data[1] = position1
        data[2] = position2
        # if position2-position1>1000:
        #    print 'current range:', position1, position2

        if contig_start[0] == contig_end[0]:
            data[0] = contig_start[0]
            renamed_data.append(data)
        else:

            # print 'new start end', position1, position2
            # print 'contig start', contig_start
            # print 'contig end', contig_end
            # print 'spanning several contigs!'
            # span across 2 contigs: make 2 coordinates (until the end of the first contig and from the begining of the second)
            data_1 = copy.copy(data)
            data_1[0] = contig_start[0]
            data_1[2] = contig_start[2]
            renamed_data.append(data_1)
            # enumerate following contigs until we match the final one
            for contig2 in following_contigs1:
                # final contig of the range, add it and break the inner loop
                if contig2[0] == contig_end[0]:
                    data_2 = copy.copy(data)
                    data_2[0] = contig_end[0]
                    # start from the first position of the second contig
                    data_2[1] = contig_end[1]
                    renamed_data.append(data_2)
                    break
                else:
                    #print contig_end
                    #print 'entire contig within the range! %s bp long' % (int(contig2[2]) - int(contig2[1])), contig2
                    # entire contig comprised within the range
                    # add it entiely to the new list
                    renamed_data.append(contig2)

        '''
        for one_contig in contig_coords:
            # within contig
            if start >= one_contig[1] and end <=one_contig[2]:
                data[0] = one_contig[0]
                renamed_data.append(data)
            # overlap between two contigs
            elif start >= one_contig[1] and start <=one_contig[2] and end >one_contig[2]:
                data_1 = data
                data_2 = data
        '''

    return renamed_data


def read_circos_file(circos_file):
    data_list = []
    with open(circos_file) as f:
        for row in f:
            data = row.rstrip().split(' ')
            if len(data) < 3:
                data = row.rstrip().split('\t')
            data_list.append(data)

    return data_list


if __name__ == '__main__':
    ###Argument handling.
    import argparse

    arg_parser = argparse.ArgumentParser(description='');
    # arg_parser.add_argument("coords_input", help="Directory to show-coords tab-delimited input file.");
    arg_parser.add_argument("-i", "--reference_karyotype", help="ref karyotype")
    arg_parser.add_argument("-t", "--target_karyotype", help="target karyotype")
    arg_parser.add_argument("-o", "--out_name", help="output name")

    args = arg_parser.parse_args()

    if not args.out_name:
        out_name = args.target_karyotype.split('.')[0] + '_renamed.' + args.target_karyotype.split('.')[1]

    with open(args.reference_karyotype, 'r') as f:
        contig_coords = []
        for row in f:
            data = row.rstrip().split(' ')
            if len(data) < 3:
                data = row.rstrip().split('\t')
            contig_coords.append([data[3], int(data[4]), int(data[5])])

    data_list = read_circos_file(args.target_karyotype)

    renamed_data = rename_karyotype(contig_coords, data_list)

    with open(out_name, 'w') as new_circos_file:
        for row in renamed_data:
            row = [str(i) for i in row]
            new_circos_file.write('\t'.join(row) + '\n')
