###################################################################
#
import os

#
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.files.storage import default_storage, Storage

#
import data_importer_logger

#
from data.models import Affymetrix, Site, Subject

##################################################################################################
# Affymetrix
##################################################################################################
# Check if affymetrix file exists in given directories. If it exists return name of file path, otherwise return False
def check_affymetrix(name, affymetrix_file_path_list):
    for file_path in affymetrix_file_path_list:
        if os.path.isfile(file_path + '/' + name):
            return file_path
    return False

# Delete affymetrix
def delete_affymetrix(name):
    try :
        affymetrix = Affymetrix.objects.get(name=name)
        path = affymetrix.cel_file.path
        default_storage.delete(path)
        affymetrix.delete()
        data_importer_logger.log_message('delete_affymetrix ----- successfully deleted affymetrix ' + name)

    except ObjectDoesNotExist:
        data_importer_logger.log_message('delete_affymetrix ----- affymetrix ' + name + ' does not exist')

# Create new affymetrix if file exists in a directory, otherwise log error
def get_affymetrix(name, subject, affymetrix_file_path_list):
    try:
        file_path = check_affymetrix(name, affymetrix_file_path_list)

        if file_path:
            cel_file = open(file_path + '/' + name, 'ro') # open given file

            affymetrix = Affymetrix(name=name, subject=subject)
            affymetrix.validate_unique()
            affymetrix.save()

            affymetrix.cel_file.storage.save('affymetrix/'+name, cel_file) # save to media directory
            affymetrix.cel_file = 'affymetrix/'+name # save cel_file
            affymetrix.save()

            cel_file.close()

            data_importer_logger.log_message('get_affymetrix ----- successfully created new affymetrix: ' + name)

            return affymetrix
 
        data_importer_logger.log_message('get_affymetrix ----- affymetrix ' + name + ' file does not exist')

    except ValidationError as e:
        data_importer_logger.log_message('get_affymetrix ----- affymetrix ' + name + ' validation error') 


##################################################################################################
# Site
##################################################################################################
# Create new site if it does not exists, otherwise return existing site
def get_site(name):
    try:
        site = Site(name=name)
        site.validate_unique()
        site.save()
        data_importer_logger.log_message('get_site ----- successfully created new site: ' + name)

    except ValidationError as e:
        site = Site.objects.get(name=name)
        data_importer_logger.log_message('get_site ----- get existing site: ' + name)

    return site

##################################################################################################
# Subject
##################################################################################################
# Delete subject
def delete_subject(genomic_db_id):
    try :
        subject = Subject.objects.get(genomic_db_id=genomic_db_id)
        subject.delete()
        data_importer_logger.log_message('delete_subject ----- successfully deleted subject ' + genomic_db_id)

    except ObjectDoesNotExist:
        data_importer_logger.log_message('delete_subject ----- subject ' + genomic_db_id + ' does not exist')

# Create new subject if it does not exists, otherwise return existing subject
def get_subject(genomic_db_id, site_id, alias, project, owner_site):
    try:
        subject = Subject(genomic_db_id=genomic_db_id, site_id=site_id, alias=alias, project=project, owner_site=owner_site)
        subject.validate_unique()
        subject.save()
        data_importer_logger.log_message('get_subject ----- successfully created new subject: ' + genomic_db_id)

    except ValidationError as e:
        subject = Subject.objects.get(genomic_db_id=genomic_db_id)
        data_importer_logger.log_message('get_subject ----- get existing subject: ' + genomic_db_id)

    return subject

# Update subject, return new if it does not exists
def update_subject(genomic_db_id, site_id, alias, project, owner_site):
    try :
        subject = Subject.objects.get(genomic_db_id=genomic_db_id)        
        subject.site_id = site_id
        subject.alias = alias
        subject.project = project
        subject.owner_site = owner_site
        subject.save()
        data_importer_logger.log_message('update_subject ----- successfully updated subject ' + genomic_db_id)

    except ObjectDoesNotExist:
        data_importer_logger.log_message('update_subject ----- subject ' + genomic_db_id + ' does not exist')
        subject = get_subject(genomic_db_id, site_id, alias, project, owner_site) 

    return subject