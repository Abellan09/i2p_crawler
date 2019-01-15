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

set_sql_debug(debug=True)


def check():
    '''
    EN: It checks if in the /finished directory there are ".fail" and/or ".ok" files to process.
    SP: Comprueba si en el directorio /finished hay ficheros ".fail" y/o ".ok" que procesar.

    It adds the names of the ".ok" and ".fail" files to the ok_files and fail_files lists, respectively.
    After that, it calls the process_fail() and process_ok() functions.
    Añade los nombres de los ficheros ".ok" y ".fail" a las listas ok_files y fail_files, respectivamente.
    A continuación, llama a las funciones process_fail() y process_ok().
    '''
    logging.debug("Dentro de check()")
    global ok_files
    global fail_files
    finished_files = os.listdir("i2p/spiders/finished")
    logging.debug("Finished Files: " + str(finished_files))
    for fil in finished_files:
        if (fil.endswith(".ok")) and (fil not in ok_files):
            ok_files.append(fil)
        elif (fil.endswith(".fail")) and (fil not in fail_files):
            fail_files.append(fil)
    # finished_files.remove(fil)
    process_fail()
    process_ok()


def process_fail():
    '''
    EN: It processes the files with ".fail" extension.
    SP: Procesa los ficheros con extensión ".fail".

    It deletes the files with the ".fail" extension from the /finished directory and adds the failed site
    to the pending_sites list so that the site can be crawled again.
    Elimina los ficheros con extensión ".fail" del directorio /finished y añade el site fallido a la lista
    pending_sites para que se vuelva a crawlear.
    '''
    logging.debug("Dentro de process_fail()")
    global fail_files
    files_to_remove = []
    logging.debug("Fail_files antes del bucle: " + str(fail_files))
    try:
        for fil in fail_files:
            files_to_remove.append(fil)
            eliminar = "i2p/spiders/ongoing/" + fil.replace(".fail", ".json")
            os.remove(eliminar)
            eliminar = "i2p/spiders/finished/" + fil
            os.remove(eliminar)

            # If the crawling process failed, there was an ERROR
            with db_session:
                dbutils.set_site_current_processing_status(s_url=fil, s_status=settings.Status.ERROR)

            logging.debug("Setting the ERROR status to site %s",fil)

    except Exception as e:
        logging.error("There has been some error with the files")
    finally:
        for i in files_to_remove:
            fail_files.remove(i)
        logging.debug("Fail_files despues del bucle: " + str(fail_files))

def process_ok():
    '''
    EN: It processes the files with ".ok" extension.
    SP: Procesa los ficheros con extensión ".ok".

    It moves the ".json" files of the sites that have been crawled correctly (.ok) from the /ongoing directory to the /finished
    directory, opens said ".json" files, calls the add_to_database() function in order to add the pertinent data to database,
    adds the sites that haven't been visited yet to the pending_sites and deletes the ".ok" files once processed.
    Mueve los ficheros ".json" de los sites que han sido crawleados correctamente (.ok) del directorio /ongoing	al directorio
    /finished, abre dichos ficheros ".json", llama a la función add_to_database() para añadir los datos pertinentes a la
    base de datos, añade a pending_sites los sites que no se hayan visitado y borra los ficheros ".ok" una vez procesados.
    '''
    logging.debug("Dentro de process_ok()")
    global ok_files

    files_to_remove = []
    logging.debug("ok_files antes del bucle: " + str(ok_files))
    try:
        for fil in ok_files:
            files_to_remove.append(fil)
            fil_without_extension = fil.replace(".ok", "")
            fil_json_extension = fil.replace(".ok", ".json")
            source = "i2p/spiders/ongoing/" + fil_json_extension
            target = "i2p/spiders/finished/" + fil_json_extension
            shutil.move(source, target)

            with open(target) as f:
                crawled_items = json.load(f)

            crawled_eepsites = crawled_items[len(crawled_items) - 1]["extracted_eepsites"]
            logging.debug("Extracted eepsites from " + fil + ": " + str(crawled_eepsites))

            # moved here to handle the status of crawled eepsites
            add_to_database(fil_without_extension, crawled_eepsites)
            eliminar = "i2p/spiders/finished/" + fil
            os.remove(eliminar)
    except:
        logging.error("There has been some error with the files")
    finally:
        for i in files_to_remove:
            ok_files.remove(i)
        logging.debug("ok_files despues del bucle: " + str(ok_files))


def add_to_database(site, targeted_sites):
    '''
    EN: It adds the extracted data by the crawler to the database.
    SP: Añade los datos extraídos por el crawler a la base de datos.

    :param site: site in question to add to the database / site en cuestión a añadir a la base de datos
    :param targeted_sites: sites to which the site points at / sitios a los que el site apunta
    '''
    logging.debug("Dentro de add_to_database()")

    try:
        with db_session:

            # Creates the src site, if needed
            dbutils.create_site(site)
            dbutils.set_site_current_processing_status(s_url=site,s_status=settings.Status.FINISHED)

            for eepsite in targeted_sites:

                # is it a new site? Create it and set up the status to pending.
                if dbutils.create_site(s_url=eepsite):
                    dbutils.set_site_current_processing_status(s_url=eepsite, s_status=settings.Status.PENDING)

                # Linking
                dbutils.create_link(site, eepsite)

    except Exception as e:
        logging.error("Something was wrong with the database")
        raise e


def run_spider(site):
    """
    Runs a spider

    :param site: str - the name of the site to be crawled
    :return: p: Popen - The subprocess status
    """

    # Try running a spider
    param1 = "url=http://" + site
    param2 = "./i2p/spiders/ongoing/" + site + ".json"
    p = subprocess.Popen(['%s/bin/scrapy' % os.environ['CONDA_PREFIX'], "crawl", "i2p", "-a", param1, "-o", param2 ], shell=False)
    p.wait()

    with db_session:
        # Create site if needed.
        dbutils.create_site(s_url=site)
        # Setting up the correct status
        dbutils.set_site_current_processing_status(s_url=site, s_status=settings.Status.ONGOING)
        # Increasing tries
        siteEntity = dbutils.increase_tries(s_url=site)

        logging.debug("Running %s, tries=%s",site,siteEntity.crawling_tries)

    return p

# Number of simultaneous spiders running
max_ongoing_spiders = 20
# Number of tries for error sites
max_crawling_tries = 2
ok_files = []
fail_files = []


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

    fh = RotatingFileHandler("registro.log", maxBytes=0, backupCount=0) # NO rotation, neither by size, nor by number of files
    fh.setFormatter(format)
    log.addHandler(fh)

    logging.debug("Dentro de main()")

    # run_spider("stats.i2p")
    # time.sleep(60)
    # exit()

    # Gets initial seeds
    seed_sites = siteutils.get_initial_seeds("../../data/seed_urls.txt")

    # Create all sites with PENDING status. Note that if the site exists, it will not be created
    with db_session:
        for site in seed_sites:
            # is it a new site? Create it and set up the status to pending.
            if dbutils.create_site(s_url=site):
                dbutils.set_site_current_processing_status(s_url=site,s_status=settings.Status.PENDING)

    # Restore processing status
    with db_session:
        # Restore previous crawling process status
        # restored pending sites
        pending_sites = dbutils.get_sites_by_processing_status(s_status=settings.Status.PENDING)
        # restored ongoing sites
        ongoing_sites = dbutils.get_sites_by_processing_status(s_status=settings.Status.ONGOING)
        # restored error sites
        error_sites = dbutils.get_sites_by_processing_status(s_status=settings.Status.ERROR)
        unknown_sites = dbutils.get_sites_by_processing_status(s_status=settings.Status.UNKNOWN) # just for debugging porpuses
        finished_sites = dbutils.get_sites_by_processing_status(s_status=settings.Status.FINISHED)# just for debugging porpuses

    logging.debug("Restoring %s ERROR sites by including then as PENDING sites.", len(error_sites))

    # Error sites should be tagged as pending sites.
    for site in error_sites:
        if site not in pending_sites:
            pending_sites.append(site)
            with db_session:
                # sets up the error site to pending siste
                dbutils.set_site_current_processing_status(s_url=site, s_status=settings.Status.PENDING)

    logging.debug("Restoring %s PENDING sites.", len(pending_sites))
    logging.debug("Restoring %s ONGOING sites.", len(ongoing_sites))

    # restored ONGOING SITES should be launched
    for site in ongoing_sites:
        if len(ongoing_sites) <= max_ongoing_spiders:
            logging.debug("Starting spider for %s.", site)
            run_spider(site)

    # Monitoring time
    stime = time.time()
    etime = time.time()

    # main loop
    while pending_sites or ongoing_sites:

        # Try to run another site
        if len(ongoing_sites) <= max_ongoing_spiders:
            if pending_sites:
                with db_session:
                    site = pending_sites.pop()
                    if dbutils.get_site(s_url=site).crawling_tries <= max_crawling_tries:
                        logging.debug("Starting spider for %s.", site)
                        run_spider(site)
                    else:
                        logging.debug("The site %s cannot be crawled.", site)
                        # The site cannot be crawled
                        dbutils.set_site_current_processing_status(s_url=site, s_status=settings.Status.UNKNOWN)

        # Polling which of the ongoing spiders is still ongoing
        check()
        time.sleep(1)
        if (etime - stime) < 60:
            etime = time.time()
        else:
            stime = time.time()
            etime = time.time()

        logging.debug("Stats --> ONGOING %s, PENDING %s, FINISHED %s, ERROR %s, UNKNOWN %s", \
                          len(ongoing_sites), len(pending_sites), len(finished_sites), len(error_sites),
                          len(unknown_sites))

        # Update the status
        with db_session:
            pending_sites = dbutils.get_sites_by_processing_status(s_status=settings.Status.PENDING)
            ongoing_sites = dbutils.get_sites_by_processing_status(s_status=settings.Status.ONGOING)
            error_sites = dbutils.get_sites_by_processing_status(s_status=settings.Status.ERROR)
            unknown_sites = dbutils.get_sites_by_processing_status(s_status=settings.Status.UNKNOWN)
            finished_sites = dbutils.get_sites_by_processing_status(s_status=settings.Status.FINISHED)

        # Error sites should be tagged as pending sites.
        for site in error_sites:
            if site not in pending_sites:
                pending_sites.append(site)
                with db_session:
                    # sets up the error site to pending siste
                    dbutils.set_site_current_processing_status(s_url=site, s_status=settings.Status.PENDING)


if __name__ == '__main__':
    main()
