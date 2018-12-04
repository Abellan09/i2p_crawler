# -*- coding: utf-8 -*-


"""
    :mod:`dbutils`
    ===========================================================================
    :synopsis: API to talk to database
    :author: Roberto Magán Carrión
    :contact: roberto.magan@uca.es, rmagan@ugr.es, robertomagan@gmail.com
    :organization: University of Cádiz, University of Granada
    :project: I2P Crawler
    :since: 0.0.1
"""
from pony.orm import *
from datetime import datetime
import entities
import settings



def add_default_info():
    """
    Adds default information to the database

    """
    # Adding site types
    add_default_site_types()
    # Adding site status
    add_default_site_status()



def add_default_site_status():
    """
    Adds default status for site crawling. (See NS_DEFAULT_INFO at settings.py)

    """
    for status in settings.NS_DEFAULT_INFO.keys():
        entities.SiteStatus(type=status, description=settings.NS_DEFAULT_INFO[status])



def add_default_site_types():
    """
    Adds default types of sites found. (See NT_DEFAULT_INFO at settings.py)

    """
    for type in settings.NT_DEFAULT_INFO.keys():
        entities.SiteType(type=type, description=settings.NT_DEFAULT_INFO[type])


# NODE ENTITY - CRUD (Create Read Update Delete)
def create_site(n_url, n_type=settings.NT_COD_I2P, n_status=settings.NS_COD_ONGOING):
    """
    Creates a new site. If no type and status is provided, I2P and Ongoing status are setup

    :param n_url: str - URL of the site, which will the name of the new site
    :param n_type: str - Type of the new site
    :param n_status: str - Processing status of the new site

    :return: Site - The new site if the site does not exist. Otherwise, return None
    """
    if not entities.Site.exists(name=n_url):
        # Gets the site type
        type = entities.SiteType.get(type=n_type)
        # Gets the processing status
        status = entities.SiteStatus.get(type=n_status)
        # Creates the new site and returns it
        return entities.Site(name=n_url, type=type, status=status)
    else:
        return None


def get_site(n_url):
    """
    Gets the site by its URL which is the name of the site

    :param n_url: str - URL/name of the site
    :return: Site - The site or None if it was not found.
    """
    # Gets the site by url
    return entities.Site.get(name=n_url)

def get_sites():
    """
    Gets all sites

    :return: list - list of sites
    """

    return entities.Site.select()[:]


def delete_site(n_url):
    """
    Deletes the site by its URL which is the name of the site if it exists.

    :param n_url: str - URL/name of the site
    """
    # Gets the site to delete
    site = entities.Site.get(name=n_url)
    # If the site exists
    if isinstance(site, entities.Site):
        site.delete()


def set_site_status(n_url, n_status=settings.NS_COD_ONGOING):
    """
    Set a new status of a site if it exists

    :param n_url: str - URL/name of the site
    :param n_status: str - The new processing status

    :return: Site - The updated site or None if the site does not exists
    """
    # Gets the site to update
    site = entities.Site.get(name=n_url)
    # If the site exists
    if isinstance(site, entities.Site):
        # Get and set the new estatus
        site.status = entities.SiteStatus.get(type=n_status)
    return site


def set_site_type(n_url, n_type=settings.NT_COD_I2P):
    """
    Set a new type of a site if it exists

    :param n_url: str - URL/name of the site
    :param n_type: str - Type of the new site

    :return: Site - The updated site or None if the site does not exists
    """
    # Gets the site to update
    site = entities.Site.get(name=n_url)
    # If the site exists
    if isinstance(site, entities.Site):
        # Get and set the new type
        site.type = entities.SiteType.get(type=n_type)
    return site


# NODE LINK STATS - CRUD (Create Read Update Delete)
def set_statistics(n_url, n_incoming, n_outgoing, n_degree):
    """
    Creates or updates site statistics

    :param n_url: str - URL/name of the site
    :param n_incoming: int - # of incoming links
    :param n_outgoing: int - # of outgoing links
    :param n_degree: int - site degree
    :return: SiteConnectivitySummary - The site statistics
    """
    # Gets the site
    site = entities.Site.get(name=n_url)
    # If the site exists
    if isinstance(site, entities.Site):
        # If the site has statistics, we are going to update values
        if isinstance(site.connectivity_summary,entities.SiteConnectivitySummary):
            site.connectivity_summary.incoming = n_incoming
            site.connectivity_summary.outgoing = n_outgoing
            site.connectivity_summary.degree = n_degree
        else:
            # set statistics
            entities.SiteConnectivitySummary(site=site, incoming=n_incoming, outgoing=n_outgoing, degree=n_degree)

    return site.connectivity_summary


def delete_statistics(n_url):
    """
    Deletes the site statistics

    :param n_url: str - URL/name of the site
    """
    # Gets the site
    site = entities.Site.get(name=n_url)
    # If the site exists
    if isinstance(site, entities.Site):
        # Delete its statistics
        site.connectivity_summary.delete()

# NODE LINKS - CRUD (Create Read Update Delete)
def create_link(sn_url, tn_url):
    """
    Creates a link if and only if both sites, source and destination site, exist.

    :param sn_url: str - URL/name of the source site
    :param tn_url: str - URL/name of the destination site
    :return: The created link or None, if the link could not be created.
    """

    # Gets source site
    s_site = entities.Site.get(name=sn_url)
    if not isinstance(s_site, entities.Site):
        # if the source site does not exists
        return None
    # Gets destination site
    t_site = entities.Site.get(name=tn_url)
    if not isinstance(t_site, entities.Site):
        # if the destination site does not exists
        return None

    # Does the link exists?
    # FIXME: Check if the link exists?
    # link = entities.Link.get(src_site=s_site)
    # if not isinstance(link, entities.Link):
    # Creates the link
    link = entities.Link(src_site=s_site, dst_site=t_site)

    return link


def get_incoming_links(tn_url):
    """
    Gets all incoming links to a destination site

    :param tn_url: str - URL/name of the destination site
    :return: list of Link
    """
    incoming = select(
        link for link in entities.Link for dst_site in link.dst_site if dst_site.name == tn_url)[:]
    return incoming


def get_outgoing_links(sn_url):
    """
    Gets all outgoing links from a source site

    :param sn_url: str - URL/name of the source site
    :return: list of Link
    """
    outgoing = select(
        link for link in entities.Link for src_site in link.src_site if src_site.name == sn_url)[:]
    return outgoing


def delete_links(n_url):
    """
    Deletes all links to and from a specific site

    :param n_url: tr - URL/name of the site
    """
    # Delete incoming links
    incoming = get_incoming_links(n_url)
    [link.delete() for link in incoming]

    # Delete outgoing links
    outgoing = get_outgoing_links(n_url)
    [link.delete() for link in outgoing]


def set_qos_to_site_by_site_name(site_name, qos):
    # Get the corresponding site
    qos = entities.SiteQoS(timestamp=datetime.today(), delay=qos)
    site = entities.Site.get(name=site_name)
    qos.site = site
