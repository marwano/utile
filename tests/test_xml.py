#!/usr/bin/env python

from unittest import TestCase, skipUnless
from utile import safe_import, pretty_xml, xml_to_dict, element_to_dict
lxml = safe_import('lxml')
mock = safe_import('mock')

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


@skipUnless(lxml, 'lxml not installed')
@skipUnless(mock, 'mock not installed')
class XMLTestCase(TestCase):
    def test_pretty_xml(self):
        self.assertEqual(pretty_xml(XML_DATA), XML_PRETTY)

    def test_element_to_dict(self):
        with mock.patch('utile.bunch_or_dict', side_effect=dict):
            actual = element_to_dict(lxml.etree.XML(XML_DATA))
            self.assertEqual(actual, XML_DICT)

    def test_xml_to_dict(self):
        with mock.patch('utile.bunch_or_dict', side_effect=dict):
            self.assertEqual(xml_to_dict(XML_DATA), XML_DICT)
