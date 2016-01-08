# 22q11-ibbc-genomic-db-utils

22q11-ibbc-genomic-db-utils contain helper programs to maintain/upload data to 22q11-ibbc-genomic-db.

# Usage

Initial Upload

    python data_importer_main.py i config.txt

Update DB

    python data_importer_main.py u config.txt

Update Affymetrix Folder

    python data_importer_main.py u config.txt

# Description of Config.txt

Tab-delimited file with information on how and what to upload

Line 1 - Absolute path of location where data_file.txt resides
Line 2 - Absolute path of Django media location
Line 3 - data_files
Line 4 - Location of raw data files

Example:

    /home/nobody/files
    /home/nobody/django/media
    /data_file_1.txt /data_file_2.txt
    /files/loc_1    /files/loc_2

# Description of data_file.txt

Tab-delimited file containing data to be uploaded to DB

Format:

    note    genomic_db_id	owner_site	alias	site_id	CEL

Example:

    note	genomic_db_id	owner_site	alias	site_id	CEL
    delete	1	somewhere	AAA,BBB	AAA	something.CEL.zip
    	2	somewhere	CCC,D	CCC	something_2.CEL.zip