#! /usr/bin/env python
#  -*- coding: utf-8 -*-

"""
    Presentation
    ============

    This is a file for to recover information from amazon filters.

"""
import re
import csv
import sys
import boto
import argparse
from boto.ec2.regioninfo import EC2RegionInfo
from boto.vpc import VPCConnection

def connect(zone, url, secret_key, access_key):
    """
        It is a function creates a connection with the boto library for communicate with instances.
        You need of more informations like:
        - API url
        - Access name
        - Region
        - Access key

    """
    try:
        region = EC2RegionInfo(name=zone, endpoint=url)
        conn = boto.vpc.VPCConnection(region=region, aws_access_key_id=access_key, aws_secret_access_key=secret_key)
    except Exception as ex:
        print ex
    return conn

def request(conn, filter_dict):
    """
        it is a function for send queries with the boto library and fill a dictionary.

    """
    try:
        conn.get_all_instances(filters=filter_dict)
        return "OK"
    except Exception as ex:
        return ex.message

def instance_filter(path):
    """
       This function fills a dictionary from a file and return the dictionary

   """
    dict_filter = {}
    with open(path, "r") as f:
          lines = f.readlines()
          for line in lines:
              if line.strip().startswith('#'):
                      continue
              reg = re.compile('([A-Za-z-./#]*).\s*=\s*(.[A-Za-z-0-9_/*]*)')
              matches =  reg.search(line)
              if matches is None :
                  continue
              key = matches.group(1)
              val = matches.group(2)
              if key not in dict_filter.keys():
                     dict_filter[key] = [val]
              elif val not in dict_filter[key]:
                     dict_filter[key].append(val)
    return dict_filter

def max_val(dict_max):
    """
        it is a function to return the maximum value of the values.

    """
    max_val =[]
    for key in dict_max.keys():
          for val in dict_max[key]:
              max_val.append(len(val))
    return max(max_val)

def max_key(dict_max):
    """
        it is a function to return the maximum value of the keys.

    """
    max_key = []
    for key in dict_max.keys():
              max_key.append(len((key)))
    return max(max_key)

def start_instance(conn, instance_id):
    """
        It is a function for start the instances.

    """
    conn.start_instances(instance_ids=instance_id)

def main(path,):
    """
        it is a function that calls all other functions and fills csv file.

    """
    try:
      with open(path, "w") as file:
        writer = csv.writer(file)
        writer.writerow(('Filter', 'value', 'Status'))
        inst = instance_filter(args.filters_file)
        max_v = max_val(inst)
        max_k = max_key(inst)
        conn = connect(args.zone, args.endpoint, args.secret_key, args.access_key)
        print "%s  %s  %s" % ("FILTER:".ljust(max_k + 5, ' '), "VALUE:".ljust(max_v + 10, ' '), "STATUS:")
        for key in inst.keys():
          for val in inst[key]:
              print   "%s  %s  %s" % (key.ljust(max_k + 5, ' '), val.ljust(max_v + 10, ' '), request(conn, {key: val}))
              writer.writerow((key, val, request(conn, {key: val})))
    finally:
       file.close()

if __name__ == '__main__':
    """
       We use here the argparse module for to manage all entries in the command line.

    """
    parser = argparse.ArgumentParser(description="Filters describes AWS")

    parser.add_argument('--zone', dest='zone', action='store',required=True,
                        help='Datacenter zone')
    parser.add_argument('--endpoint', dest='endpoint', action='store', required=True,
                        default='api.outscale.com',
                        help='EC2 API endpoint (default:api.outscale.com)')
    parser.add_argument('--access-key', dest='access_key', action='store',required=True,
                        help='EC2 access key')
    parser.add_argument('--secret-key', dest='secret_key', action='store',required=True,
                        help='EC2 secret key')
    parser.add_argument('--filters-file', dest='filters_file', action='store',required=True,
                        help='The file with all filters')
    parser.add_argument('--export-as-csv', dest='export_as_csv', action='store',required=True,
                        default=" ",
                        help='For export in the csv file')
    args = parser.parse_args()

    main(args.export_as_csv)