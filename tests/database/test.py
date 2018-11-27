import unittest
from pony.orm import *
from crawler.i2p.database import dbutils, entities, settings
from crawler.i2p import manager

class DatabaseTests(unittest.TestCase):

    def setUp(self):
        rollback()
        db_session.__enter__()
        sql_debug(True)
        # Adding default info to the database
        dbutils.add_default_info()

    def tearDown(self):
        # Comment to persist the test in the database
        rollback()
        db_session.__exit__()

    def test_addtodabase(self):

        # Example data to test
        # crawled eepsite
        site = "i2p_src.i2p"
        # outgoing eepsites of site
        extracted_eepsites =  ["i2p-projekt.i2p", "trac.i2p2.i2p", "www.i2p2.i2p", "ugha.i2p", "z-lab.i2p", "zab.i2p",
                                "legwork.i2p", "i2pwiki.i2p", "cases.i2p"]

        # Number of links to be created
        links_to_create = len(extracted_eepsites)

        # Call to the method under test
        manager.add_to_database(site,extracted_eepsites)

        # Gets the outgoing links from site to the extracted ones
        created_links = len(dbutils.get_outgoing_links(site))

        self.assertEqual(len(dbutils.get_nodes()),10,msg="The number of created nodes should be 10")
        self.assertEqual(links_to_create, created_links, msg="The number of links should be 9")

if __name__ == '__main__':
    unittest.main()
