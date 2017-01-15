#!/usr/bin/env python
'''
Module: es-extract
Desc: Extract ARIB closed caption info from a previously demuxed Elementary Stream
Author: John O'Neil
Email: oneil.john@gmail.com
DATE: Saturday January 14th 2017

'''
import os
import sys
import argparse

from mpeg.ts import TS
from mpeg.ts import ES

from arib.closed_caption import next_data_unit
from arib.closed_caption import StatementBody
import arib.code_set as code_set
import arib.control_characters as control_characters
from arib.data_group import DataGroup
from arib.data_group import next_data_group


DISPLAYED_CC_STATEMENTS = [
  code_set.Kanji,
  code_set.Alphanumeric,
  code_set.Hiragana,
  code_set.Katakana,
  control_characters.APS,
  control_characters.MSZ,
  control_characters.NSZ,
  control_characters.SP,
  control_characters.SSZ,
  control_characters.CS,
  control_characters.CSI,
  #control_characters.COL,
  control_characters.BKF,
  control_characters.RDF,
  control_characters.GRF,
  control_characters.YLF,
  control_characters.BLF,
  control_characters.MGF,
  control_characters.CNF,
  control_characters.WHF,
  #control_characters.TIME,
]

def formatter(statements, timestamp):
  '''Turn a list of decoded closed caption statements
    into something we want (probably just plain text)
    Note we deal with unicode only here.
  '''
  print('File elapsed time seconds: {s}'.format(s=timestamp))
  line = u''.join([unicode(s) for s in statements if type(s) in DISPLAYED_CC_STATEMENTS])
  return line

# GLOBALS TO KEEP TRACK OF STATE
VERBOSE = True
SILENT = False
DEBUG = False

def main():
  global elapsed_time_s
  global VERBOSE
  global SILENT

  parser = argparse.ArgumentParser(description='Draw CC Packets from MPG2 Transport Stream file.')
  parser.add_argument('infile', help='Input filename (MPEG2 Transport Stream File)', type=str)
  parser.add_argument('-p', '--pid', help='Specify a PID of a PES known to contain closed caption info (tool will attempt to find the proper PID if not specified.).', type=int, default=-1)
  args = parser.parse_args()

  infilename = args.infile
  pid = args.pid

  if not os.path.exists(infilename):
    print 'Input filename :' + infilename + " does not exist."
    os.exit(-1)

  for data_group in next_data_group(infilename):
    try:
      if not data_group.is_management_data():
        #We now have a Data Group that contains caption data.
        #We take out its payload, but this is further divided into 'Data Unit' structures
        caption = data_group.payload()
        #iterate through the Data Units in this payload via another generator.
        for data_unit in next_data_unit(caption):
          #we're only interested in those Data Units which are "statement body" to get CC data.
          if not isinstance(data_unit.payload(), StatementBody):
            return

          #formatter function above. This dumps the basic text to stdout.
          cc = formatter(data_unit.payload().payload(), 0)
          if cc and VERBOSE:
            #according to best practice, always deal internally with UNICODE, and encode to
            #your encoding of choice as late as possible. Here, i'm encoding as UTF-8 for
            #my command line.
            #DECODE EARLY, ENCODE LATE
            print(cc.encode('utf-8'))
    except:
      pass


 
if __name__ == "__main__":
  main()