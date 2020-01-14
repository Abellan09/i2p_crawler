# -*- coding: utf-8 -*-

"""
    :mod:`site_connectivity`
    ===========================================================================
    :synopsis: offline inter-site connectivity
    :author: Roberto Magán Carrión
    :contact: roberto.magan@uca.es, rmagan@ugr.es, robertomagan@gmail.com
    :organization: University of Cádiz, University of Granada
    :project: I2P Crawler
    :since: 0.0.1
"""

from pony.orm import sql_debug, db_session
from database import dbsettings
from database import dbutils


# sql_debug(True)


def set_connectivity():
    """
    Updates the connectivity summary tables.
    """
    with db_session:
        finished_sites = dbutils.get_sites_by_processing_status(dbsettings.Status.FINISHED)

    for site in finished_sites:
        print("ID {0} - {1}".format(site.id, site.name))
        set_site_connectivity_summary(site.name, site.pages)

    print("TOTAL sites found {0}".format(len(finished_sites)))


def set_site_connectivity_summary(site, pages):
    with db_session:
        n_incoming_links = len(dbutils.get_incoming_links(site))
        n_outgoing_links = len(dbutils.get_outgoing_links(site))
        degree = n_incoming_links
        print(
        "Adding connectivity summary to {0}, in_links: {1}, out_links: {2}, degree: {3}, out_pages_links: {4}".format(
            site, n_incoming_links, n_outgoing_links, degree, pages))
        dbutils.set_connectivity_summary(s_url=site, n_incoming=n_incoming_links, n_outgoing=n_outgoing_links,
                                         n_degree=degree, n_pages=pages)


def export_links():
    """
    Export in CSV format the links (edges) among sites.
    """
    with db_session:
        links = dbutils.get_links()

        for link in links:
            print("{0} - {1}".format(link.src_site.id, link.dst_site.id))
            #print("{0}{1} --> {1}{2}".format(link.src_site.id, link.src_site.name, link.dst_site.id, link.dst_site.name))

    print("TOTAL links found {0}".format(len(links)))

def main():
    #set_connectivity()
    export_links()


if __name__ == '__main__':
    main()
