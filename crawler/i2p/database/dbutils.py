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
from pony.orm import select
from datetime import datetime
import entities
import settings


# NODE ENTITY - CRUD (Create Read Update Delete)
def create_site(s_url, s_type=settings.Type.I2P):
    """
    Creates a new site. If no type and status is provided, I2P and ONGOING status are setup

    :param s_url: str - URL of the site, which will the name of the new site
    :param s_type: str - Type of the new site

    :return: Site - The new site if the site does not exist. Otherwise, return None
    """

    # TODO: create Exception hierarchy.
    assert isinstance(s_type, settings.Type), 'Not valid type of site'

    # The new Site
    site = None

    if not entities.Site.exists(name=s_url):
        # Gets the site type
        new_type = entities.SiteType.get(type=s_type.name)

        # Creates the new site
        site = entities.Site(name=s_url, type=new_type)

    return site


def get_site(s_url):
    """
    Gets the site by its URL which is the name of the site

    :param s_url: str - URL/name of the site
    :return: Site - The site or None if it was not found.
    """
    # Gets the site by url
    return entities.Site.get(name=s_url)


def get_sites():
    """
    Gets all sites

    :return: list - list of sites
    """

    return entities.Site.select()[:]


def delete_site(s_url):
    """
    Deletes the site by its URL which is the name of the site if it exists.

    :param s_url: str - URL/name of the site
    """
    # Gets the site to delete
    site = entities.Site.get(name=s_url)
    # If the site exists
    if isinstance(site, entities.Site):
        site.delete()


def set_site_type(s_url, s_type):
    """
    Set a new type of a site if it exists

    :param s_url: str - URL/name of the site
    :param s_type: str - Type of the new site

    :return: Site - The updated site or None if the site does not exists
    """

    # TODO: create Exception hierarchy.
    assert isinstance(s_type, settings.Type), 'Not valid type of site'

    # Gets the site to update
    site = entities.Site.get(name=s_url)
    # If the site exists
    if isinstance(site, entities.Site):
        # Get and set the new type
        site.type = entities.SiteType.get(type=s_type.name)
    return site


def increase_tries(s_url):
    """
    Increasing the counter of crawling tries

    :param s_url: str - URL/name of the site
    :return: Site - The updated site or None if the site does not exists
    """

    # Gets the site to update
    site = entities.Site.get(name=s_url)

    # If the site exists
    if isinstance(site, entities.Site):
        # increasing the tries
        site.crawling_tries = site.crawling_tries + 1

    return site


# NODE LINK STATS - CRUD (Create Read Update Delete)
def set_statistics(s_url, n_incoming, n_outgoing, n_degree):
    """
    Creates or updates site statistics

    :param s_url: str - URL/name of the site
    :param n_incoming: int - # of incoming links
    :param n_outgoing: int - # of outgoing links
    :param n_degree: int - site degree
    :return: SiteConnectivitySummary - The site statistics
    """
    # Gets the site
    site = entities.Site.get(name=s_url)
    # If the site exists
    if isinstance(site, entities.Site):
        # If the site has statistics, we are going to update values
        if isinstance(site.connectivity_summary, entities.SiteConnectivitySummary):
            site.connectivity_summary.incoming = n_incoming
            site.connectivity_summary.outgoing = n_outgoing
            site.connectivity_summary.degree = n_degree
        else:
            # set statistics
            entities.SiteConnectivitySummary(site=site, incoming=n_incoming, outgoing=n_outgoing, degree=n_degree)

    return site.connectivity_summary


def delete_statistics(s_url):
    """
    Deletes the site statistics

    :param s_url: str - URL/name of the site
    """
    # Gets the site
    site = entities.Site.get(name=s_url)
    # If the site exists
    if isinstance(site, entities.Site):
        # Delete its statistics
        site.connectivity_summary.delete()


# NODE LINKS - CRUD (Create Read Update Delete)
def create_link(src_url, dst_url):
    """
    Creates a link if and only if both sites, source and destination site, exist.

    :param src_url: str - URL/name of the source site
    :param dst_url: str - URL/name of the destination site
    :return: The created link or None, if the link could not be created.
    """

    # Gets source site
    s_site = entities.Site.get(name=src_url)
    if not isinstance(s_site, entities.Site):
        # if the source site does not exists
        return None
    # Gets destination site
    t_site = entities.Site.get(name=dst_url)
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


def get_incoming_links(ts_url):
    """
    Gets all incoming links to a destination site

    :param ts_url: str - URL/name of the destination site
    :return: list of Link
    """
    incoming = select(
        link for link in entities.Link for dst_site in link.dst_site if dst_site.name == ts_url)[:]
    return incoming


def get_outgoing_links(ss_url):
    """
    Gets all outgoing links from a source site

    :param ss_url: str - URL/name of the source site
    :return: list of Link
    """
    outgoing = select(
        link for link in entities.Link for src_site in link.src_site if src_site.name == ss_url)[:]
    return outgoing


def delete_links(s_url):
    """
    Deletes all links to and from a specific site

    :param s_url: str - URL/name of the site
    """
    # Delete incoming links
    incoming = get_incoming_links(s_url)
    [link.delete() for link in incoming]

    # Delete outgoing links
    outgoing = get_outgoing_links(s_url)
    [link.delete() for link in outgoing]


# NODE PROCESSING LOG - CRUD
def create_processing_log(s_url,s_status=settings.Status.PENDING):
    """
    Creates a new crawler processing status. Default status PENDING

    :param s_url: str - URL/name of the site
    :param s_status: str - The chosen processing status
    :return: SiteProcessingLog - The new processing status log
    """

    # is the status valid?
    assert isinstance(s_status, settings.Status), 'Not valid type of status'

    # Gets the chosen status
    new_status = entities.SiteStatus.get(type=s_status.name)

    # Creates the new processing status
    return entities.SiteProcessingLog(site=get_site(s_url=s_url), status=new_status, timestamp=datetime.today())


def get_all_processing_log():

    """
    Gets all processing log

    :return: list - All processing logs
    """

    return entities.SiteProcessingLog.select()[:].to_list()


# NODE PROCESSING STATUS - CRUD
def get_sites_by_processing_status(s_status):
    """

    Gets sites by processing status

    :param s_status: str - The chosen processing status
    :return: sites: list of str - The url of the sites in status ``s_status``
    """
    assert isinstance(s_status, settings.Status), 'Not valid type of status'

    sites = select(site.name for site in entities.Site if site.current_processing_status.type is s_status.name)[:].to_list()

    return sites


def set_site_current_processing_status(s_url, s_status, add_processing_log=True):
    """
    Creates and sets a new processing status to a site.

    :param s_url: str - URL/name of the site
    :param s_status: str - The chosen processing status
    :param add_processing_log: bool - When True a new procession log is added.
    :return: site: Site - The updated Site with the updated corresponding processing status.
    """

    # Gets the site
    site = entities.Site.get(name=s_url)
    # If the site exists
    if isinstance(site, entities.Site):
        # Creates and set the new processing status
        site.current_processing_status = entities.SiteStatus.get(type=s_status.name)

        if add_processing_log:
            # Adds a new processing log
            create_processing_log(s_url,s_status)

    return site


# NODE QoS - CRUD
def set_qos(s_url, s_qos):
    """
    Sets a new QoS to the site if existing

    :param s_url: str - URL/name of the site
    :param s_qos: float - QoS value
    :return: Site - The updated site or None if not existing.
    """

    assert isinstance(s_qos, float), 'QoS value must be float'

    # Gets sites_url
    site = entities.Site.get(name=s_url)
    if isinstance(site, entities.Site):
        # Creates new QoS value
        qos = entities.SiteQoS(timestamp=datetime.today(), delay=s_qos)
        site.qos = qos
    return site


# NODE language - CRUD
def set_site_language(s_url, s_language, l_engine):
    """
    Creates a new crawler processing status. Default status PENDING

    :param s_url: str - URL/name of the site
    :param s_language: str - The inferred language
    :param l_engine: str - Engine used to inferred the site's language.
    :return: SiteLanguage - The new language for the site
    """

    # Creates the new language
    return entities.SiteLanguage(site=get_site(s_url=s_url), language=s_language, engine=l_engine)