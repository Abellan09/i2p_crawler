# encoding: utf-8

import os			# https://docs.python.org/2/library/os.html
import shutil		# https://docs.python.org/2/library/shutil.html
import time			# https://docs.python.org/2/library/time.html
import subprocess	# https://docs.python.org/2/library/subprocess.html
import json			# https://docs.python.org/2/library/json.html
import logging		# https://docs.python.org/2/library/logging.html
import sys
import shlex
import signal
import traceback
import threading
import psutil

from pony.orm import db_session, set_sql_debug
from database import dbutils
from database import dbsettings
from utils import siteutils
from i2pthread import discoverythread
from logging.handlers import RotatingFileHandler
from i2p import i2psettings

# Config params
# Number of simultaneous spiders running
MAX_ONGOING_SPIDERS = 5
# Number of tries for error sites
MAX_CRAWLING_TRIES_ON_ERROR = 2
# Number of tries to discover a site
MAX_CRAWLING_TRIES_ON_DISCOVERING = 5
# Number of tries for error sites
MAX_DURATION_ON_DISCOVERING = 10  # Minutes
# Number of parallel single threads running
MAX_SINGLE_THREADS_ON_DISCOVERING = 10
# Http response timeout
HTTP_TIMEOUT = 30  # Seconds
# Initial seeds
INITIAL_SEEDS = "seed_urls_200.txt"

# Set to True to show pony SQL queries
set_sql_debug(debug=False)

# scrapy processes launched by the manager.
# {site:subproces}
alive_spiders = {}


def check_crawling_status():
    '''
    EN: It checks if in the /finished directory there are ".fail" and/or ".ok" files to process.
    SP: Comprueba si en el directorio /finished hay ficheros ".fail" y/o ".ok" que procesar.

    It adds the names of the ".ok" and ".fail" files to the ok_spiders and fail_spiders lists, respectively.
    After that, it calls the process_fail() and process_ok() functions.
    Añade los nombres de los ficheros ".ok" y ".fail" a las listas ok_spiders y fail_spiders, respectivamente.
    A continuación, llama a las funciones process_fail() y process_ok().
    '''

    # init list
    ok_spiders = []
    fail_spiders = []

    logging.info("Checking spiders status ...")

    finished_files = os.listdir(i2psettings.PATH_FINISHED_SPIDERS)

    logging.debug("Files in finished folder #%s", len(finished_files))

    for fil in finished_files:
        if (fil.endswith(".ok")) and (fil not in ok_spiders):
            ok_spiders.append(fil)
        elif (fil.endswith(".fail")) and (fil not in fail_spiders):
            fail_spiders.append(fil)
            
    if fail_spiders:
        process_fail(fail_spiders)
    if ok_spiders:
        process_ok(ok_spiders)

def check_spiders_status():

    """
    Checks the status integrity among the launched scrapy sub-processes and their status in DB. It is preventing from
    zombie/defunc processes that never update their status in DB, remaining in ONGOING forever.

    Differences between status in DB and the real alive spider processes, tell us what were the crashed spiders.
    """

    with db_session:
        ongoing_db_sites = dbutils.get_sites_by_processing_status(dbsettings.Status.ONGOING)

        logging.debug("There are %s ongoing sites in db and %s alive spider processes.",
                      len(ongoing_db_sites),
                      len(alive_spiders))

        for site in ongoing_db_sites:
            p_status = psutil.Process(alive_spiders[site].pid).status()
            logging.debug("Spider/Site %s is %s.", site, p_status)
            del p_status
            # Is it not running?
            if (site not in alive_spiders.keys()) or (alive_spiders[site].poll() is not None):
                dbutils.set_site_current_processing_status(s_status=dbsettings.Status.ERROR_DEFUNC, s_url=site)
                alive_spiders.pop(site)
                # TODO: remove the ongoing *.json file?




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
            eliminar = i2psettings.PATH_ONGOING_SPIDERS + fil.replace(".fail", ".json")
            os.remove(eliminar)
            eliminar = i2psettings.PATH_FINISHED_SPIDERS + fil
            os.remove(eliminar)

    except Exception as e:
        logging.error("ERROR processing FAILED file - %s", e)

    finally:
        with db_session:
            for fil in files_to_remove:
                # If the crawling process failed, there was an ERROR
                site = fil.replace(".fail", "")
                dbutils.set_site_current_processing_status(s_url=site, s_status=dbsettings.Status.ERROR)
                logging.debug("Setting the ERROR status to site %s", site)
                # This process should not be alive
                if site in alive_spiders.keys():
                    alive_spiders.pop(site)
                    logging.debug("Removing %s from alive spiders.")

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
            source = i2psettings.PATH_ONGOING_SPIDERS + fil_json_extension
            target = i2psettings.PATH_FINISHED_SPIDERS + fil_json_extension
            shutil.move(source, target)


            # Once a site has been crawled, what we only need is the extracted eepsite which are at the end of the
            # json file
            #last_lines = siteutils.tail(target, n=2)
            #last_lines = last_lines.replace('\n]','')
            with open(target,'r') as f:
                crawled_items = json.loads(f.readline())

            crawled_eepsites = crawled_items["extracted_eepsites"]
            logging.debug("Extracted eepsites from " + fil + ": " + str(crawled_eepsites))

            with db_session:
                # setting up the language
                set_site_language(current_site_name, crawled_items["language"])

                # setting up the home site info
                set_site_home_info(current_site_name, crawled_items["size_main_page"], crawled_items["title"][0])

                # moved here to handle the status of crawled eepsites
                link_eepsites(current_site_name, crawled_eepsites)

                # setting up connectivity summary
                # TODO this method should be called separately once the crawling process finished to get real values of in, out and degree
                set_site_connectivity_summary(current_site_name, crawled_items["total_eepsite_pages"])

                # setting up the number of pages to the site.
                set_site_number_pages(current_site_name, crawled_items["total_eepsite_pages"])

    except Exception as e:
        logging.error("ERROR processing OK file %s - %s",current_site_name, e)
        # If an error is raised, this site should be tagged as ERROR
        with db_session:
            dbutils.set_site_current_processing_status(s_url=current_site_name, s_status=dbsettings.Status.ERROR)
            # This process should not be alive
            if current_site_name in alive_spiders.keys():
                alive_spiders.pop(current_site_name)
                logging.debug("Removing %s from alive spiders.")

        # removing the JSON file for the site which causes the error.
        eliminar = i2psettings.PATH_FINISHED_SPIDERS + fil_json_extension
        os.remove(eliminar)

    finally:
        # Delete *.ok files in finished folder
        for fil in ok_spiders:
            eliminar = i2psettings.PATH_FINISHED_SPIDERS + fil
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
            dbutils.set_site_current_processing_status(s_url=site, s_status=dbsettings.Status.FINISHED)
            logging.debug("Site %s was setup to FINISHED.", site)

            # This process should not be alive
            if site in alive_spiders.keys():
                alive_spiders.pop(site)
                logging.debug("Removing %s from alive spiders.")

            for eepsite in targeted_sites:

                # is it a new site? Create it and set up the status to pending.
                if dbutils.create_site(s_url=eepsite):
                    dbutils.set_site_current_processing_status(s_url=eepsite, s_status=dbsettings.Status.DISCOVERING)

                # Linking
                dbutils.create_link(site, eepsite)

                logging.debug("New link: %s --> %s",site,eepsite)

    except Exception as e:
        logging.error("ERROR linking eepsites")
        logging.error("ERROR: %s", e)


def set_site_language(site, languages):
    """

    Keeps the site language/s considering all the available language engines.

    :param site: str - Site url
    :param languages: dict - {engine_n:lang_inferred} For each engine, the inferred language
    """

    logging.info("Setting languages ...")

    with db_session:
        for engine in languages.keys():
            logging.debug("Adding language to %s: %s,%s ", site, engine, languages[engine])
            dbutils.set_site_language(s_url=site, s_language=languages[engine], l_engine=engine)


def set_site_home_info(site, size_main_page, title):
    """

    Creates the home info for a site.

    :param site: str - Site url
    :param size_main_page: dict - {LETTERS:n_letters,WORDS:n_words,IMAGES:n_images,SCRIPTS:n_scripts} Found in the home of a site
    :param title: str - the found title in the home page
    """

    logging.info("Setting home info ...")

    with db_session:
        logging.debug("Adding info to %s: letters: %s, words: %s, images: %s, scripts: %s, title: %s ",
                      site,
                      size_main_page['LETTERS'],
                      size_main_page['WORDS'],
                      size_main_page['IMAGES'],
                      size_main_page['SCRIPTS'],
                      title)
        dbutils.set_site_home_info(s_url=site,
                                   s_letters=size_main_page['LETTERS'],
                                   s_words=size_main_page['WORDS'],
                                   s_images=size_main_page['IMAGES'],
                                   s_scripts=size_main_page['SCRIPTS'],
                                   s_title=title)


def set_site_number_pages(site, pages):
    """

    Updates the site to add the number of found pages

    :param site: str - Site url
    :param pages: int - The number of site pages
    """

    logging.info("Setting number of pages ...")

    with db_session:
        logging.debug("Updating number of pages %s to site %s: ", pages, site)
        dbutils.set_site_number_of_pages(s_url=site, n_pages=pages)


def set_site_connectivity_summary(site, pages):
    """

    Creates a connectivity summary info which adds/updates incoming, outgoing, n of html pages to external sites, and degree

    :param site: str - Site url
    :param pages: int - The number of site pages
    """

    logging.info("Setting connectivity summary info ...")

    with db_session:
        n_incoming_links = len(dbutils.get_incoming_links(site))
        n_outgoing_links = len(dbutils.get_outgoing_links(site))
        degree = n_incoming_links
        logging.debug("Adding connectivity summary to %s, in_links: %s, out_links: %s, degree: %s, out_pages_links: %s", site, n_incoming_links, n_outgoing_links, degree, pages)
        dbutils.set_connectivity_summary(s_url=site, n_incoming=n_incoming_links, n_outgoing=n_outgoing_links, n_degree=degree, n_pages=pages)


def run_spider(site):
    """
    Runs a spider

    :param site: str - the name of the site to be crawled
    :return: p: Popen - The subprocess status
    """

    # TODO each spider process should be better monitored. Maybe launching them in separated threads.

    # Try running a spider
    command = 'scrapy crawl i2p -a url="http://' + site + '"'
    p = subprocess.Popen(shlex.split(command))

    logging.debug("Command launched %s",shlex.split(command))

    with db_session:
        # Create site if needed.
        dbutils.create_site(s_url=site)
        # Setting up the correct status
        dbutils.set_site_current_processing_status(s_url=site, s_status=dbsettings.Status.ONGOING)
        # Increasing tries
        siteEntity = dbutils.increase_tries_on_error(s_url=site)

        logging.debug("Process launched for %s with PID=%s, tries=%s",site,p.pid,siteEntity.error_tries)

    return p



def error_to_pending(error_sites, pending_sites):
    """
    ERROR sites are set up to PENDING if the max crawling tries are not exceeded.

    :param error_sites: list - List of current ERROR sites
    :param pending_sites: list - List of current PENDING sites
    """

    # Error sites should be tagged as pending sites.
    with db_session:
        for site in error_sites:
            if dbutils.get_site(s_url=site).error_tries < MAX_CRAWLING_TRIES_ON_ERROR:
                logging.debug("The site %s has been restored. New status PENDING.", site)
                pending_sites.insert(0, site)
                # sets up the error site to pending status
                dbutils.set_site_current_processing_status(s_url=site, s_status=dbsettings.Status.PENDING)
            else:
                logging.debug("The site %s cannot be crawled because the number of max_tries on ERROR status has been reached.", site)
                logging.debug("Setting up the DISCOVERING status to %s",site)
                # The site cannot be crawled
                dbutils.set_site_current_processing_status(s_url=site, s_status=dbsettings.Status.DISCOVERING)
                dbutils.reset_tries_on_error(s_url=site)


def get_sites_from_floodfill():

    """
    Creates new sites from floodfill sites

    """

    # Gets initial seeds
    seed_sites = siteutils.get_seeds_from_file(i2psettings.PATH_DATA + "floodfill_seeds.txt")

    # Create all sites in DISCOVERING status. Note that if the site exists, it will not be created
    with db_session:
        for site in seed_sites:
            # is it a new site? Create it and set up the status to pending.
            if dbutils.create_site(s_url=site):
                dbutils.set_site_current_processing_status(s_url=site, s_status=dbsettings.Status.DISCOVERING)


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

    fh = RotatingFileHandler(i2psettings.PATH_LOG + "i2pcrawler.log", maxBytes=0, backupCount=0) # NO rotation, neither by size, nor by number of files
    fh.setFormatter(format)
    log.addHandler(fh)

    logging.info("Starting I2P Darknet crawling ... ")

    try:

        # Gets initial seeds
        seed_sites = siteutils.get_seeds_from_file(i2psettings.PATH_DATA + INITIAL_SEEDS)

        # Create all sites in DISCOVERING status. Note that if the site exists, it will not be created
        with db_session:
            for site in seed_sites:
                # is it a new site? Create it and set up the status to pending.
                if dbutils.create_site(s_url=site):
                    dbutils.set_site_current_processing_status(s_url=site, s_status=dbsettings.Status.DISCOVERING)

        # Create all sites in DISCOVERING status obtained from floodfill seeds.
        get_sites_from_floodfill()

        # Restoring the crawling status
        status = siteutils.get_crawling_status()
        # restored pending sites
        pending_sites = status[dbsettings.Status.PENDING.name]
        # restored ongoing sites
        ongoing_sites = status[dbsettings.Status.ONGOING.name]
        # restored error sites
        error_sites = status[dbsettings.Status.ERROR.name]
        # restored discovering sites
        discovering_sites = status[dbsettings.Status.DISCOVERING.name]

        logging.debug("Restoring %s ERROR sites.", len(error_sites))

        # Getting error sites and setting up them to pending to be crawled again.
        error_to_pending(error_sites, pending_sites)

        logging.debug("Restoring %s PENDING sites.", len(pending_sites))
        logging.debug("Restoring %s ONGOING sites.", len(ongoing_sites))
        logging.debug("Restoring %s DISCOVERING sites.", len(discovering_sites))

        # restored ONGOING SITES should be launched
        for site in ongoing_sites:
            if len(ongoing_sites) <= MAX_ONGOING_SPIDERS:
                logging.debug("Starting spider for %s.", site)
                p = run_spider(site)
                # To monitor all the running spiders
                alive_spiders[site] = p


        # Discovering time
        stime = time.time()
        etime = time.time()

        # discoverying thread
        logging.debug("Running discovering process ...")
        dThread = discoverythread.DiscoveringThread(MAX_CRAWLING_TRIES_ON_DISCOVERING,
                                                    MAX_DURATION_ON_DISCOVERING,
                                                    MAX_SINGLE_THREADS_ON_DISCOVERING,
                                                    HTTP_TIMEOUT)
        dThread.setName('DiscoveryThread')
        dThread.start()

        # main loop
        while pending_sites or ongoing_sites or discovering_sites:

            # Try to run another site
            if len(ongoing_sites) < MAX_ONGOING_SPIDERS:
                if pending_sites:
                    with db_session:
                        site = pending_sites.pop()
                        if dbutils.get_site(s_url=site).error_tries < MAX_CRAWLING_TRIES_ON_ERROR:
                            logging.debug("Starting spider for %s.", site)
                            p = run_spider(site)
                            # To monitor all the running spiders
                            alive_spiders[site] = p
                        else:
                            logging.debug("The site %s cannot be crawled because the number of max_tries on ERROR status has been reached.",site)
                            logging.debug("Setting up the DISCOVERING status to %s", site)
                            # The site
                            dbutils.set_site_current_processing_status(s_url=site, s_status=dbsettings.Status.DISCOVERING)
                            dbutils.reset_tries_on_error(s_url=site)

            # Polling how the crawling of spiders is going ...
            check_crawling_status()

            # Checking spiders status coherence between DB and the launched processes.
            check_spiders_status()

            # Adding new sites to DISCOVERING status obtained from floodfill seeds.
            get_sites_from_floodfill()

            # Get current status
            status = siteutils.get_crawling_status()
            pending_sites = status[dbsettings.Status.PENDING.name]
            ongoing_sites = status[dbsettings.Status.ONGOING.name]
            error_sites = status[dbsettings.Status.ERROR.name]
            discarded_sites = status[dbsettings.Status.DISCARDED.name]
            finished_sites = status[dbsettings.Status.FINISHED.name]
            discovering_sites = status[dbsettings.Status.DISCOVERING.name]

            # Getting error sites and setting up them to pending to be crawled again.
            error_to_pending(error_sites, pending_sites)

            logging.debug("Stats --> ONGOING %s, PENDING %s, FINISHED %s, ERROR %s, DISCOVERING %s, DISCARDED %s", \
                          len(ongoing_sites), len(pending_sites), len(finished_sites), len(error_sites), len(discovering_sites),
                          len(discarded_sites))

            time.sleep(1)
            if (etime - stime) < 2:
                etime = time.time()
            else:
                stime = time.time()
                etime = time.time()

    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received ...")
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=5, file=sys.stdout)
    finally:
        logging.info("Stopping all services ...")

        try:
            if isinstance(dThread, discoverythread.DiscoveringThread): dThread.stop()
        except UnboundLocalError:
            logging.warning("DiscoveringThread is not running, so it will not stopped.")

        for i in threading.enumerate():
            if i is not threading.currentThread():
                logging.debug("Waiting for %s thread ...", i.name)
                i.join()
        logging.info("Exiting ...")
        exit(1)


def signal_handler(signum, frame):
    """
    Manages Ctrl+C interruption signal

    :param signum: signal
    :param frame:
    """
    if signum == signal.SIGINT:
        raise KeyboardInterrupt, "Signal Interrupt"
    else:
        logging.debug("Signal handler do not recognize signal number %s", signum)


if __name__ == '__main__':
    # SIGINT registration to manage them outside
    signal.signal(signal.SIGINT, signal_handler)

    main()
