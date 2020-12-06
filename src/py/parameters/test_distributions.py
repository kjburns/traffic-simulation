import unittest
from tempfile import NamedTemporaryFile
from lxml import etree
from simulator.default_xml_files import DefaultXmlFiles
from parameters.distributions import Distributions
import os


class TestsForDistributions(unittest.TestCase):
    def test_that_invalid_document_raises_exception(self):
        temp_file_path: str

        with NamedTemporaryFile(delete=False) as fp:
            document_root: etree.ElementBase = etree.parse(DefaultXmlFiles.DISTRIBUTIONS_FILE).getroot()
            first_child: etree.ElementBase = document_root[0]
            document_root.remove(first_child)
            fp.write(etree.tostring(document_root))
            temp_file_path = fp.name
            fp.close()

        def thrower():
            Distributions.process_file(temp_file_path)

        try:
            self.assertRaises(RuntimeError, thrower)
        finally:
            os.remove(temp_file_path)


class TestsForConnectorLinkSelectionBehavior(unittest.TestCase):

    def test_default_values(self):
        pass


if __name__ == '__main__':
    unittest.main()
