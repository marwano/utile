#!/usr/bin/env python

from unittest import TestCase, skipUnless
from utile import pretty_xml, xml_to_dict, element_to_dict
from support import etree

XML_DATA = "<html><body><h1>test1</h1><h2>test2</h2></body></html>"
XML_PRETTY = """\
<html>
  <body>
    <h1>test1</h1>
    <h2>test2</h2>
  </body>
</html>
"""
XML_DICT = {'body': {'h2': 'test2', 'h1': 'test1'}}


@skipUnless(etree, 'lxml not installed')
class XMLTestCase(TestCase):
    def test_pretty_xml(self):
        self.assertEqual(pretty_xml(XML_DATA), XML_PRETTY)

    def test_element_to_dict(self):
        self.assertEqual(element_to_dict(etree.XML(XML_DATA)), XML_DICT)

    def test_xml_to_dict(self):
        self.assertEqual(xml_to_dict(XML_DATA), XML_DICT)
