import sys
import argparse
import configparser
import logging
import os.path
from azure.storage.blob import BlobServiceClient, ContainerClient, BlobClient

logging.basicConfig(
    filename="azlogging.log",
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',)


def listb(args, containerclient):
    """ This function shows our blob list file"""
    logging.info('Blob list file')
    blob_list=containerclient.list_blobs()
    for blob in blob_list:
        print(blob.name)



def upload(cible, blobclient):
    """ this function uploads to blob storage account a file """
    logging.info('opening azuretest.txt file to be sent to azfiles container')
    with open(cible, "rb") as f:
        logging.warning('Uploding file to the container')
        blobclient.upload_blob(f)
        


def download(filename, dl_folder, blobclient):
    """ this function download a file from my blob storage account to save it in local in download folder"""
    logging.info('opening azuretest.txt to be downloaded from azfile container')
    with open(os.path.join(dl_folder,filename), "wb") as my_blob:
        logging.warning('downloading file from the container')
        blob_data=blobclient.download_blob()
        blob_data.readinto(my_blob)


def main(args,config):
    """ this fonction is the heart of our scrip
        it executes the fonction entered in our command line
    """
    logging.info('main fonction')
    blobclient=BlobServiceClient(
        f"https://{config['storage']['account']}.blob.core.windows.net",
        config["storage"]["key"],
        logging_enable=False)
    logging.debug('connecting to the stockage account')
    containerclient=blobclient.get_container_client(config["storage"]["container"])
    logging.debug('connecting to the container')
    if args.action=="list":
        logging.debug("List argument choosen, executing List fonction")
        return listb(args, containerclient)
    else:
        if args.action=="upload":
            blobclient=containerclient.get_blob_client(os.path.basename(args.cible))
            logging.debug("arg upload, executing upload fonction")
            return upload(args.cible, blobclient)
        elif args.action=="download":
            logging.debug("arg download . executing download fonction")
            blobclient=containerclient.get_blob_client(os.path.basename(args.remote))
            logging.warning("Downloading file")
            return download(args.remote, config["general"]["restoredir"], blobclient)
    

if __name__=="__main__":
    parser=argparse.ArgumentParser("Logiciel d'archivage de documents")
    parser.add_argument("-cfg",default="config.ini",help="chemin du fichier de configuration")
    parser.add_argument("-lvl",default="info",help="niveau de log")
    subparsers=parser.add_subparsers(dest="action",help="type d'operation")
    subparsers.required=True
    
    parser_s=subparsers.add_parser("upload")
    parser_s.add_argument("cible",help="fichier à envoyer")

    parser_r=subparsers.add_parser("download")
    parser_r.add_argument("remote",help="nom du fichier à télécharger")
    parser_r=subparsers.add_parser("list")

    args=parser.parse_args()

    #erreur dans logging.warning : on a la fonction au lieu de l'entier
    loglevels={"debug":logging.DEBUG, "info":logging.INFO, "warning":logging.WARNING, "error":logging.ERROR, "critical":logging.CRITICAL}
    print(loglevels[args.lvl.lower()])
    logging.basicConfig(level=loglevels[args.lvl.lower()])

    config=configparser.ConfigParser()
    config.read(args.cfg)

    sys.exit(main(args,config))
