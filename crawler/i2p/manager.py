# encoding: utf-8

import os			# https://docs.python.org/2/library/os.html
import shutil		# https://docs.python.org/2/library/shutil.html
import time			# https://docs.python.org/2/library/time.html
import subprocess	# https://docs.python.org/2/library/subprocess.html
import json			# https://docs.python.org/2/library/json.html
import logging		# https://docs.python.org/2/library/logging.html
import sys

from pony.orm import db_session, set_sql_debug
from database import dbutils
from database import settings
from utils import siteutils
from logging.handlers import RotatingFileHandler

# Config params
# Number of simultaneous spiders running
MAX_ONGOING_SPIDERS = 10
# Number of tries for error sites
MAX_CRAWLING_TRIES = 2
# Set to True to show pony SQL queries
set_sql_debug(debug=False)

ok_spiders = []
fail_spiders = []


def check_spiders_status(ok_spiders, fail_spiders):
    '''
    EN: It checks if in the /finished directory there are ".fail" and/or ".ok" files to process.
    SP: Comprueba si en el directorio /finished hay ficheros ".fail" y/o ".ok" que procesar.

    It adds the names of the ".ok" and ".fail" files to the ok_spiders and fail_spiders lists, respectively.
    After that, it calls the process_fail() and process_ok() functions.
    Añade los nombres de los ficheros ".ok" y ".fail" a las listas ok_spiders y fail_spiders, respectivamente.
    A continuación, llama a las funciones process_fail() y process_ok().
    '''

    logging.info("Checking spiders status ...")

    finished_files = os.listdir("i2p/spiders/finished")
    logging.debug("Files in finished folder #%s: %s", len(finished_files),str(finished_files))
    for fil in finished_files:
        if (fil.endswith(".ok")) and (fil not in ok_spiders):
            ok_spiders.append(fil)
        elif (fil.endswith(".fail")) and (fil not in fail_spiders):
            fail_spiders.append(fil)
            
    if fail_spiders:
        process_fail(fail_spiders)
    if ok_spiders:
        process_ok(ok_spiders)


def process_fail(fail_spiders):
    '''
    EN: It processes the files with ".fail" extension.
    SP: Procesa los ficheros con extensión ".fail".

    It deletes the files with the ".fail" extension from the /finished directory and adds the failed site
    to the pending_sites list so that the site can be crawled again.
    Elimina los ficheros con extensión ".fail" del directorio /finished y añade el site fallido a la lista
    pending_sites para que se vuelva a crawlear.
    '''
    logging.info("Processing FAILED spiders ... ")

    files_to_remove = []
    logging.debug("Starting to process FAILED spiders #%s: %s", len(fail_spiders), str(fail_spiders))
    try:
        for fil in fail_spiders:
            files_to_remove.append(fil)
            eliminar = "i2p/spiders/ongoing/" + fil.replace(".fail", ".json")
            os.remove(eliminar)
            eliminar = "i2p/spiders/finished/" + fil
            os.remove(eliminar)

    except Exception as e:
        logging.error("ERROR processing FAILED files ")
        logging.error("ERROR: %s", e)

    finally:
        with db_session:
            for fil in files_to_remove:
                fail_spiders.remove(fil)
                # If the crawling process failed, there was an ERROR
                site = fil.replace(".fail", "")
                dbutils.set_site_current_processing_status(s_url=site, s_status=settings.Status.ERROR)
                logging.debug("Setting the ERROR status to site %s", site)

        logging.debug("Ending to process FAILED spiders #%s: %s", len(fail_spiders), str(fail_spiders))


def process_ok(ok_spiders):
    '''
    EN: It processes the files with ".ok" extension.
    SP: Procesa los ficheros con extensión ".ok".

    It moves the ".json" files of the sites that have been crawled correctly (.ok) from the /ongoing directory to the /finished
    directory, opens said ".json" files, calls the link_eepsites() function in order to add the pertinent data to database,
    adds the sites that haven't been visited yet to the pending_sites and deletes the ".ok" files once processed.
    Mueve los ficheros ".json" de los sites que han sido crawleados correctamente (.ok) del directorio /ongoing	al directorio
    /finished, abre dichos ficheros ".json", llama a la función link_eepsites() para añadir los datos pertinentes a la
    base de datos, añade a pending_sites los sites que no se hayan visitado y borra los ficheros ".ok" una vez procesados.
    '''
    logging.info("Processing OK spiders ...")

    files_to_remove = []
    logging.debug("Starting to process OK spiders #%s: %s", len(ok_spiders), str(ok_spiders))

    # Used in case of error to setup in BBDD as ERROR
    current_site_name = None

    try:
        for fil in ok_spiders:
            files_to_remove.append(fil)
            current_site_name = fil.replace(".ok", "")
            fil_json_extension = fil.replace(".ok", ".json")
            source = "i2p/spiders/ongoing/" + fil_json_extension
            target = "i2p/spiders/finished/" + fil_json_extension
            shutil.move(source, target)

            with open(target) as f:
                crawled_items = json.load(f)

            crawled_eepsites = crawled_items[len(crawled_items) - 1]["extracted_eepsites"]
            logging.debug("Extracted eepsites from " + fil + ": " + str(crawled_eepsites))

            # moved here to handle the status of crawled eepsites
            link_eepsites(current_site_name, crawled_eepsites)

    except Exception as e:
        logging.error("ERROR processing file %s",current_site_name)
        logging.error("ERROR: %s",e)
        # If an error is raised, this site should be tagged as ERROR
        with db_session:
            dbutils.set_site_current_processing_status(s_url=current_site_name, s_status=settings.Status.ERROR)
    finally:
        for i in files_to_remove:
            ok_spiders.remove(i)
        eliminar = "i2p/spiders/finished/" + fil
        os.remove(eliminar)
        logging.debug("Ending to process OK spiders #%s: %s", len(ok_spiders), str(ok_spiders))


def link_eepsites(site, targeted_sites):
    '''
    EN: It adds the extracted data by the crawler to the database.
    SP: Añade los datos extraídos por el crawler a la base de datos.

    :param site: site in question to add to the database / site en cuestión a añadir a la base de datos
    :param targeted_sites: sites to which the site points at / sitios a los que el site apunta
    '''
    logging.info("Linking eepsites ...")

    try:
        with db_session:

            logging.debug("Linking %s to %s ", site, targeted_sites)

            # Creates the src site, if needed
            dbutils.create_site(site)
            dbutils.set_site_current_processing_status(s_url=site,s_status=settings.Status.FINISHED)

            for eepsite in targeted_sites:

                # is it a new site? Create it and set up the status to pending.
                if dbutils.create_site(s_url=eepsite):
                    dbutils.set_site_current_processing_status(s_url=eepsite, s_status=settings.Status.PENDING)

                # Linking
                dbutils.create_link(site, eepsite)

                logging.debug("New link: %s --> %s",site,eepsite)

    except Exception as e:
        logging.error("ERROR linking eepsites")
        logging.error("ERROR: %s", e)


def run_spider(site):
    """
    Runs a spider

    :param site: str - the name of the site to be crawled
    :return: p: Popen - The subprocess status
    """

    # TODO each spider process should be better monitored. Maybe launching them in separated threads.

    # Try running a spider
    param1 = "url=http://" + site
    param2 = "./i2p/spiders/ongoing/" + site + ".json"
    p = subprocess.Popen(["scrapy", "crawl", "i2p", "-a", param1, "-o", param2], shell=False)

    with db_session:
        # Create site if needed.
        dbutils.create_site(s_url=site)
        # Setting up the correct status
        dbutils.set_site_current_processing_status(s_url=site, s_status=settings.Status.ONGOING)
        # Increasing tries
        siteEntity = dbutils.increase_tries(s_url=site)

        logging.debug("Running %s, tries=%s",site,siteEntity.crawling_tries)

    return p


def get_crawling_status():
    """
    Gets a snapshot of how the crawling procedure is going

    :return: status: dict - The current crawling status
    """

    status = {}

    with db_session:
        status[settings.Status.PENDING.name] = dbutils.get_sites_by_processing_status(s_status=settings.Status.PENDING)
        status[settings.Status.ONGOING.name] = dbutils.get_sites_by_processing_status(s_status=settings.Status.ONGOING)
        status[settings.Status.ERROR.name] = dbutils.get_sites_by_processing_status(s_status=settings.Status.ERROR)
        status[settings.Status.DISCARDED.name] = dbutils.get_sites_by_processing_status(s_status=settings.Status.DISCARDED)
        status[settings.Status.FINISHED.name] = dbutils.get_sites_by_processing_status(s_status=settings.Status.FINISHED)

    return status


def error_to_pending(error_sites, pending_sites):
    """
    ERROR sites are set up to PENDING if the max crawling tries are not exceeded.

    :param error_sites: list - List of current ERROR sites
    :param pending_sites: list - List of current PENDING sites
    """

    # Error sites should be tagged as pending sites.
    with db_session:
        for site in error_sites:
            if dbutils.get_site(s_url=site).crawling_tries <= MAX_CRAWLING_TRIES:
                logging.debug("The site %s has been restored. New status PENDING.", site)
                pending_sites.insert(0, site)
                # sets up the error site to pending status
                dbutils.set_site_current_processing_status(s_url=site, s_status=settings.Status.PENDING)
            else:
                logging.debug("The site %s cannot be crawled because the number of max_tries has been reached.", site)
                # The site cannot be crawled
                dbutils.set_site_current_processing_status(s_url=site, s_status=settings.Status.DISCARDED)


def main():
    '''
    EN: It controls the whole process of the crawling through a loop that is repeated every 2 seconds.
    SP: Controla todo el proceso del crawling mediante un bucle que se repite cada 2 segundos.

    Every second it enters the main loop (if there are still sites to visit or sites that are been visited) to crawl all the sites.
    Finally, the extracted info is added to the database and the json file that will be used for web visualitation of the node map is generated.
    Cada segundo se entra en el bucle principal (si quedan sitios por visitar o se están visitando) para crawlear todos los sites.
    Finalmente, la información extraída se añade a la base de datos y se genera el archivo json que se utilizará para la visulación web del mapa de nodos.
    '''

    log = logging.getLogger('')
    log.setLevel(logging.DEBUG)
    format = logging.Formatter('%(asctime)s %(levelname)s - %(threadName)s - mod: %(module)s, method: %(funcName)s, msg: %(message)s')

    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)

    fh = RotatingFileHandler("../../logs/i2pcrawler.log", maxBytes=0, backupCount=0) # NO rotation, neither by size, nor by number of files
    fh.setFormatter(format)
    log.addHandler(fh)

    logging.debug("Dentro de main()")

    # run_spider("stats.i2p")
    # time.sleep(60)
    # exit()

    # Gets initial seeds
    seed_sites = siteutils.get_initial_seeds("../../data/seed_urls.txt")
    #seed_sites = []

    # Create all sites with PENDING status. Note that if the site exists, it will not be created
    with db_session:
        for site in seed_sites:
            # is it a new site? Create it and set up the status to pending.
            if dbutils.create_site(s_url=site):
                dbutils.set_site_current_processing_status(s_url=site,s_status=settings.Status.PENDING)

    # Restoring the crawling status
    status = get_crawling_status()
    # restored pending sites
    pending_sites = status[settings.Status.PENDING.name]
    # restored ongoing sites
    ongoing_sites = status[settings.Status.ONGOING.name]
    # restored error sites
    error_sites = status[settings.Status.ERROR.name]

    logging.debug("Restoring %s ERROR sites.", len(error_sites))

    # Getting error sites and setting up them to pending to be crawled again.
    error_to_pending(error_sites, pending_sites)

    logging.debug("Restoring %s PENDING sites.", len(pending_sites))
    logging.debug("Restoring %s ONGOING sites.", len(ongoing_sites))

    # restored ONGOING SITES should be launched
    for site in ongoing_sites:
        if len(ongoing_sites) <= MAX_ONGOING_SPIDERS:
            logging.debug("Starting spider for %s.", site)
            run_spider(site)

    # Monitoring time
    stime = time.time()
    etime = time.time()

    # main loop
    while pending_sites or ongoing_sites:

        # Try to run another site
        if len(ongoing_sites) <= MAX_ONGOING_SPIDERS:
            if pending_sites:
                with db_session:
                    site = pending_sites.pop()
                    if dbutils.get_site(s_url=site).crawling_tries <= MAX_CRAWLING_TRIES:
                        logging.debug("Starting spider for %s.", site)
                        run_spider(site)
                    else:
                        logging.debug("The site %s cannot be crawled.", site)
                        # The site cannot be crawled
                        dbutils.set_site_current_processing_status(s_url=site, s_status=settings.Status.DISCARDED)

        # Polling how spiders are going ...
        check_spiders_status(ok_spiders, fail_spiders)

        time.sleep(1)
        if (etime - stime) < 60:
            etime = time.time()
        else:
            stime = time.time()
            etime = time.time()

        # Get current status
        status = get_crawling_status()
        pending_sites = status[settings.Status.PENDING.name]
        ongoing_sites = status[settings.Status.ONGOING.name]
        error_sites = status[settings.Status.ERROR.name]
        discarded_sites = status[settings.Status.DISCARDED.name]
        finished_sites = status[settings.Status.FINISHED.name]

        # Getting error sites and setting up them to pending to be crawled again.
        error_to_pending(error_sites, pending_sites)

        logging.debug("Stats --> ONGOING %s, PENDING %s, FINISHED %s, ERROR %s, DISCARDED %s", \
                      len(ongoing_sites), len(pending_sites), len(finished_sites), len(error_sites),
                      len(discarded_sites))


if __name__ == '__main__':
    main()
