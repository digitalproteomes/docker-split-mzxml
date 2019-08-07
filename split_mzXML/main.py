#!/usr/bin/env python

"Split mzXML files base on filter line"

from __future__ import division
from __future__ import print_function
import re
import argparse
import xml.etree.ElementTree as ET
from subprocess import call

ET.register_namespace('', "http://sashimi.sourceforge.net/schema_revision/mzXML_3.1")
ns = {'mzxml': 'http://sashimi.sourceforge.net/schema_revision/mzXML_3.1'}


def filter_scan(scan, filter_pattern, parent):
  """ Remove MS2 scans without filter_pattern from xml tree
  """
  filter_line = scan.get('filterLine')
  filter_m = re.search(filter_pattern, filter_line)
  if filter_m is None:
    parent.remove(scan)
    return 0
  else:
    return 1


def findall_rec(node, element='mzxml:scan'):
  """Recursively finds all elements element under current node (not
  only direct children)

  Yields a list of parent element and scan element
  """
  for item in node.findall(element, ns):
    yield [node, item]
    for parent, child in findall_rec(item, element):
      yield [parent, child]


def parse_mzxml(xml, filter_pattern, scan_levels, renumber):
  """ Parse mzXML file and apply filtering as requested
  """
  scan_count = 0
  tree = ET.parse(xml)
  root = tree.getroot()

  for run in root.findall('mzxml:msRun', ns):
    for parent, scan in findall_rec(run):
      if int(scan.get('msLevel')) in scan_levels:
        scan_count += filter_scan(scan, filter_pattern, parent)
      else:
        scan_count += 1
      if renumber:
        scan.set('num', str(scan_count))
    run.set('scanCount', str(scan_count))
  return tree


def save_mzxml(tree, out_mzxml):
  """ Save filtered mzXML tree
  """
  tree.write(out_mzxml, encoding='ISO-8859-1', xml_declaration=True)
  call(["indexmzXML", out_mzxml])
  call(["mv", out_mzxml + '.new', out_mzxml])


def parse_args():
  """ Parse user parameters
  """
  parser = argparse.ArgumentParser(description='Filter mzXML files')
  parser.add_argument('--input', help='Path to the input mzXML file', required=True)
  parser.add_argument('--output', help='Path to the output mzXML file', required=True)
  parser.add_argument('--pattern', help='Pattern that must be present in the MS2 scans filter line',
                      required=True)
  parser.add_argument('--scan_levels', nargs='+', type=int, default=[2],
                      help="""List of MS levels to which the filter is applied
                              (all other levels are left untouched)""")
  parser.add_argument('--renumber', action='store_true', help='Sequentially renumbers scans')
  return parser.parse_args()


def main():
  """ Main """
  args = parse_args()

  xml = args.input
  filter_pattern = args.pattern
  out_mzxml = args.output
  scan_levels = args.scan_levels
  renumber = args.renumber

  tree = parse_mzxml(xml, filter_pattern, scan_levels, renumber)
  save_mzxml(tree, out_mzxml)


if __name__ == "__main__":
  main()
