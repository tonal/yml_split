#!/usr/bin/env python
# -*- coding: utf-8 -*-
u'''
Разбиение файлов XML формата Яндекс.Маркет на куски по указанномк количеству
записей о товарных позициях.

Copyright (C) 2011  Alexandr N. Zamaraev (aka tonal)

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from copy import deepcopy
import logging
from optparse import OptionParser
import os.path as osp
import sys

from lxml import etree

def main(opts, uris):
  for uri in uris:
    tree, offers = load_xml(uri)
    fname = osp.basename(uri)
    (fname, ext) = osp.splitext(fname)
    ext = ext[1:]
    templ = opts.templ.replace('%fname', fname).replace('%ext', ext)
    #save_xml(tree, templ, 0)
    split_loop(opts, tree, offers, templ)

def split_loop(opts, tree, offers, templ):
  new_tree, new_offers = copy_new(tree)
  num = opts.num
  cnt = 0
  all_cnt = len(offers)
  saved_cnt = 0
  offer = offers.find('offer')
  while offer is not None:
    cnt += 1
    saved_cnt += 1
    new_offers.append(offer)
    if cnt % num == 0:
      save_xml(new_tree, templ % (cnt // num))
      logging.info('save %d from %d to %s', saved_cnt, all_cnt, templ % (cnt // num))
      new_tree, new_offers = copy_new(tree)
      saved_cnt = 0
      all_cnt = len(offers)
    offer = offers.find('offer')
  if cnt % num != 0:
    save_xml(new_tree, templ % (cnt // num))
    logging.info('save %d from %d to %s', saved_cnt, all_cnt, templ % (cnt // num))

def load_xml(uri):
  tree = etree.parse(uri) #'http://epool.ru/include/cash/yml.xml')
  logging.info('parsed: %s', uri)
  root = tree.getroot()
  offers = root.find('shop/offers')
  shop = offers.getparent()
  shop.remove(offers)
  shop.text = u'\n'
  shop.append(etree.Element('offers'))
  noffs = shop.find('offers')
  noffs.text = u'\n'
  noffs.tail = u'\n'
  return tree, offers

def copy_new(tree):
  new_tree = deepcopy(tree)
  root = new_tree.getroot()
  new_offers = root.find('shop/offers')
  return new_tree, new_offers

def save_xml(tree, name):
  datas = etree.tostring(
    tree, pretty_print=True, encoding='utf-8', xml_declaration=True)
  open(name, "w").writelines(datas)

def __parse_opt():
  parser = OptionParser(usage='usage: %prog [options] url or file')
  #parser.add_option(
  #  "-t", "--out", dest="tag", default='offers',
  #  help="tag for split [default: %default]")
  parser.add_option(
    "-n", "--num", dest="num", type='int', default=2000,
    help="num offer in output file [default: %default]")
  parser.add_option(
    "-f", "--ftempl", dest="templ", default="%fname.%d.%ext",
    help="template for output file names [default: %default]")
  parser.add_option(
    "-l", "--log", dest="log", default="",
    help="log LFILE [default: %default]", metavar="LFILE")
  parser.add_option(
    "-q", "--quiet", action="store_true", dest="quiet", default=False,
    help="don't print status messages to stdout")
  parser.add_option(
    '-v', '--verbose', action='store_true', dest='verbose', default=False,
    help='print verbose status messages to stdout')
  parser.add_option(
    '', '--version', action='store_true', dest='version', default=False,
    help='print version and license to stdout')
  (options, args) = parser.parse_args()
  return options, args

def print_version():
  print 'License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>'

def __init_log(opts):
  u'Настройка лога'
  format = '%(asctime)s %(levelname)-8s %(message)s'
  datefmt = '%Y-%m-%d %H:%M:%S'
  level = logging.DEBUG if opts.verbose else (
    logging.WARNING if opts.quiet else logging.INFO)
  logging.basicConfig(
    level=level,
    format=format, datefmt=datefmt)
  if not opts.log:
    return
  log = logging.FileHandler(opts.log, 'a', 'utf-8')
  log.setLevel(level) #logging.INFO) #DEBUG) #
  formatter = logging.Formatter(fmt=format, datefmt=datefmt)
  log.setFormatter(formatter)
  logging.getLogger('').addHandler(log)

if __name__ == '__main__':
  opts, args = __parse_opt()
  if opts.version:
    print_version()
  else:
    __init_log(opts)
    if not args:
      args = ['yml.xml']
    main(opts, args)
