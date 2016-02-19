###################################################################
import os, sys, csv, string, zipfile
from os.path import basename
import django
import distutils.util

# Setup environ
sys.path.append('../22q11-ibbc-genomic-db/22q11-ibbc')
os.environ['DJANGO_SETTINGS_MODULE'] = "22q11-ibbc.settings.local"

# Core Django imports
from django.contrib.auth.models import User

import data_importer_data, data_importer_logger

django.setup()

#######################################################################################
# Initial Insert
def initial_insert(file_path, data_file, affymetrix_file_path_list):
    data_importer_logger.log_message('initial_insert ----- with file: ' + data_file)

    with open(data_file, 'rb') as f:
        raw_data = [row for row in csv.reader(f.read().splitlines(), delimiter="\t")]

        for row in range(1, len(raw_data)):
            #read data info
            note = raw_data[row][0]
            genomic_db_id = raw_data[row][1]
            owner_site = raw_data[row][2]
            alias = raw_data[row][3]
            site_id = raw_data[row][4]
            affymetrix_name = raw_data[row][5]

            data_importer_logger.log_message('initial_insert ----- processing genomic_db_id: ' + genomic_db_id)

            owner_site_instance = data_importer_data.get_site(owner_site)

            if 'delete' in note.lower():
                data_importer_logger.log_message('initial_insert ----- delete or deleted in note of genomic_db_id: ' + genomic_db_id)

            else:
                subject = data_importer_data.get_subject(genomic_db_id, site_id, alias, 'ibbc', owner_site_instance)

                if affymetrix_name:
                    data_importer_data.get_affymetrix(affymetrix_name, subject, affymetrix_file_path_list)


#######################################################################################
# Update data
def update_data(file_path, data_file, affymetrix_file_path_list):
    data_importer_logger.log_message('update_data ----- with file: ' + data_file)

    with open(data_file, 'rb') as f:
        raw_data = [row for row in csv.reader(f.read().splitlines(), delimiter="\t")]

        for row in range(1, len(raw_data)):
            #read data info
            note = raw_data[row][0]
            genomic_db_id = raw_data[row][1]
            owner_site = raw_data[row][2]
            alias = raw_data[row][3]
            site_id = raw_data[row][4]
            affymetrix_name = raw_data[row][5]

            data_importer_logger.log_message('update_data ----- processing genomic_db_id: ' + genomic_db_id)

            owner_site_instance = data_importer_data.get_site(owner_site)

            if 'delete' in note.lower():
                data_importer_logger.log_message('update_data ----- delete or deleted in note of genomic_db_id: ' + genomic_db_id)
                data_importer_data.delete_subject(genomic_db_id)

            else:
                subject = data_importer_data.update_subject(genomic_db_id, site_id, alias, 'ibbc', owner_site_instance)

                if affymetrix_name:
                    data_importer_data.delete_affymetrix(affymetrix_name)
                    data_importer_data.get_affymetrix(affymetrix_name, subject, affymetrix_file_path_list)


#######################################################################################
# Update affymetrix folders
def update_affymetrix_folder(file_path, data_file, affymetrix_file_path_list, upload_file_path):
    data_importer_logger.log_message('update_affymetrix_folder ----- with file: ' + data_file)

    with open(data_file, 'rb') as f:
        raw_data = [row for row in csv.reader(f.read().splitlines(), delimiter="\t")]

        folder_dict = {}

        # Create folder and copy all zip files into it
        for row in range(1, len(raw_data)):
            #read data info
            note = raw_data[row][0]
            genomic_db_id = raw_data[row][1]
            owner_site = raw_data[row][2]
            alias = raw_data[row][3]
            site_id = raw_data[row][4]
            affymetrix_name = raw_data[row][5]

            data_importer_logger.log_message('update_affymetrix_folder ----- processing genomic_db_id: ' + genomic_db_id)

            owner_site_instance = data_importer_data.get_site(owner_site)
            folder, tmp_holder = owner_site_instance.folder.split('.')
            directory = upload_file_path + '/tmp/' + folder
            if not os.path.exists(directory):
                os.makedirs(directory)
                data_importer_logger.log_message('update_affymetrix_folder ----- creating directory: ' + directory)

            # collect all the folder names
            if not folder_dict.has_key(folder):
                folder_dict[folder] = ''

            if 'delete' not in note.lower():
                if affymetrix_name:
                    
                    data_importer_logger.log_message('update_affymetrix_folder ----- processing affymetrix: ' + affymetrix_name)

                    new_file_path = data_importer_data.check_affymetrix(affymetrix_name, affymetrix_file_path_list)
                    if new_file_path:
                        data_importer_logger.log_message('update_affymetrix_folder ----- copying affymetrix: ' + affymetrix_name)
                        shutil.copy2(new_file_path + '/' + affymetrix_name, directory)    

    # if affymetrix_folder does not exists, create one
    affymetrix_folder_path = upload_file_path + '/affymetrix_folder'
    if not os.path.exists(affymetrix_folder_path):
        data_importer_logger.log_message('update_affymetrix_folder ----- creating affymetrix_folder')
        os.makedirs(affymetrix_folder_path)

    # For each folder created, zip it, copy it to live directory and remove temporary directory
    for directory in folder_dict:
        # Remove old archive
        if os.path.exists(affymetrix_folder_path + '/' + directory + '.zip'):
            data_importer_logger.log_message('update_affymetrix_folder ----- removing existing affymetrix folder: ' + directory + '.zip')
            os.remove(affymetrix_folder_path + '/' + directory + '.zip')

        # Compress
        data_importer_logger.log_message('update_affymetrix_folder ----- compressing affymetrix folder: ' + directory)
        #shutil.make_archive(upload_file_path + '/tmp/' + directory, 'zip', upload_file_path + '/tmp/' + directory)

        zip_directory = upload_file_path + '/tmp/' + directory

        with zipfile.ZipFile(zip_directory + '.zip', "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
            path = os.path.normpath(zip_directory)
            zf.write(path, basename(path))

            for dirpath, dirnames, filenames in os.walk(zip_directory):
                for name in sorted(dirnames):
                    path = os.path.normpath(os.path.join(dirpath, name))
                    zf.write(path, basename(path))
                for name in filenames:
                    path = os.path.normpath(os.path.join(dirpath, name))
                    if os.path.isfile(path):
                        zf.write(path, basename(path))

        # Move archive to live directory
        data_importer_logger.log_message('update_affymetrix_folder ----- moving affymetrix folder: ' + directory + '.zip')
        shutil.move(upload_file_path + '/tmp/' + directory + '.zip', affymetrix_folder_path)

        # Remove temporary directory for site
        if os.path.exists(upload_file_path + '/tmp/' + directory):
            data_importer_logger.log_message('update_affymetrix_folder ----- remove temporary directory: ' + directory)
            shutil.rmtree(upload_file_path + '/tmp/' + directory)

    # Remove temporary directory
    if os.path.exists(upload_file_path + '/tmp'):
        data_importer_logger.log_message('update_affymetrix_folder ----- remove temporary directory')
        shutil.rmtree(upload_file_path + '/tmp')

#######################################################################################
# Main
def main():

    if len(sys.argv) > 1:
        try:
            infile = open(sys.argv[2])
            raw = infile.readlines()
            infile.close()

            file_path = string.strip(raw[0])
            upload_file_path = string.strip(raw[1])
            file_list = string.split(string.strip(raw[2]))
            affymetrix_file_path_list = string.split(string.strip(raw[3]))

            if sys.argv[1] == 'i': # initial load
                for csv_file in file_list:
                    initial_insert(file_path, file_path + csv_file, affymetrix_file_path_list)
            elif sys.argv[1] == 'u': # update db
                for csv_file in file_list:
                    update_data(file_path, file_path + csv_file, affymetrix_file_path_list)
            elif sys.argv[1] == 'f': # update affymetrix folder
                for csv_file in file_list:
                    update_affymetrix_folder(file_path, file_path + csv_file, affymetrix_file_path_list, upload_file_path)
            else:
                sys.exit('Check arguments - option not defined')

        except OSError:
            sys.exit('Check arguments - config file not found')

    else:
        sys.exit('Check arguments - option(i, u, f) config_file')

if __name__=="__main__":
    main()
