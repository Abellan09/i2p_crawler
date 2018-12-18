import unittest
from pony.orm import *
from crawler.i2p.database import populate, dbutils, entities, settings
from crawler.i2p import manager
import time


class CrawlerTests(unittest.TestCase):

    def setUp(self):
        rollback()
        db_session.__enter__()
        sql_debug(True)
        # Adding default info to the database
        # Comment if it is has already been populated
        populate.add_default_info()

    def tearDown(self):
        # Comment to persist the test in the database
        rollback()
        db_session.__exit__()

    def addtodabase(self):

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

        self.assertEqual(len(dbutils.get_sites()),10,msg="The number of created sites should be 10")
        self.assertEqual(links_to_create, created_links, msg="The number of links should be 9")

class DatabaseTests(unittest.TestCase):

    def setUp(self):
        rollback()
        db_session.__enter__()
        sql_debug(True)
        # Adding default info to the database
        # Comment if the database has already been populated
        populate.add_default_info()

    def tearDown(self):
        # Comment to persist the test in the database
        rollback()
        db_session.__exit__()

    def test_create_site(self):

        # Example data to test
        # crawled eepsite
        site = "i2p_src.i2p"

        new_site = dbutils.create_site(s_url=site)

        self.assertIsNotNone(new_site,msg="The site has not been created")

    def test_processing_status_log(self):
        # creates different sites with different processing log status and sets the current status.
        #first site
        one_site_pending = dbutils.create_site(s_url="one_site.i2p")
        dbutils.set_site_current_processing_status(s_url="one_site.i2p", s_status=settings.Status.PENDING)
        time.sleep(1)
        # updates the first status to ONGOING
        dbutils.set_site_current_processing_status(s_url="one_site.i2p", s_status=settings.Status.ONGOING)
        time.sleep(1)

        #second site
        two_site_pending = dbutils.create_site(s_url="two_site.i2p")
        dbutils.set_site_current_processing_status(s_url="two_site.i2p", s_status=settings.Status.PENDING)
        time.sleep(1)
        # updates the second site status to ONGOING
        dbutils.set_site_current_processing_status(s_url="two_site.i2p", s_status=settings.Status.ONGOING)
        time.sleep(1)
        # updates the second site status to FINISHED
        dbutils.set_site_current_processing_status(s_url="two_site.i2p", s_status=settings.Status.FINISHED)
        time.sleep(1)

        #third site
        three_site_pending = dbutils.create_site(s_url="three_site.i2p")
        dbutils.set_site_current_processing_status(s_url="three_site.i2p", s_status=settings.Status.PENDING)
        time.sleep(1)

        #fourth site
        four_site_error = dbutils.create_site(s_url="four_site.i2p")
        dbutils.set_site_current_processing_status(s_url="four_site.i2p", s_status=settings.Status.ERROR,add_processing_log=False)

        # get all ongoing sites
        all_ongoing_sites = dbutils.get_sites_by_processing_status(s_status=settings.Status.ONGOING)
        self.assertEqual(len(all_ongoing_sites), 1, msg="Just only one site should be ONGOING")

        # get all pending sites
        all_pending_sites = dbutils.get_sites_by_processing_status(s_status=settings.Status.PENDING)
        self.assertEqual(len(all_pending_sites), 1, msg="Just only one site should be PENDING")

        # get all finished sites
        all_finished_sites = dbutils.get_sites_by_processing_status(s_status=settings.Status.FINISHED)
        self.assertEqual(len(all_finished_sites), 1, msg="Just only one site should be FINISHED")

        # get all error sites
        all_error_sites = dbutils.get_sites_by_processing_status(s_status=settings.Status.PENDING)
        self.assertEqual(len(all_error_sites), 1, msg="Just only one site should be ERROR")

        #Checks the number of processing logs added
        all_processing_log =dbutils.get_all_processing_log()
        self.assertEqual(len(all_processing_log), 6, msg="Only 6 processing log entries should be found in SiteProcessingLog")


if __name__ == '__main__':
    unittest.main()
