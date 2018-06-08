import json

import psycopg2
import psycopg2.extras
import requests


def upload_file(solr_url, filepath):
    if filepath.endswith(".csv"):
        url = solr_url + '/update?commit=true'
        headers = {
            'Content-type': 'application/csv',
        }
    elif filepath.endswith(".json"):
        url = solr_url + '/update?commit=true'
        headers = {
            'Content-type': 'application/json',
        }
    else:
        return "Could not upload. Unsupported file type. Currently only CSV and JSON files are supported."

    data = open(filepath, 'rb').read()
    response = requests.post(url, headers=headers, data=data)
    print(response.status_code)
    print(response.reason)

    if response.status_code == 200:
        reponse_message = "Successfully uploaded file to Solr."
    elif response.status_code == 400:
        reponse_message = "Could not upload. Check file."
    else:
        reponse_message = "Could not upload. Contact Admin."

    return reponse_message


def ohdsi_upload_from_db(conn_string, solr_url):
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    report_list = []
    url = solr_url + '/update/json'
    headers = {
        'Content-type': 'application/json',
    }

    cursor.execute("""SELECT * FROM mimic_v5.note""")
    result = cursor.fetchall()
    for i in result:
        concept_id = int(i[4])
        cursor.execute("""SELECT concept_name FROM mimic_v5.concept WHERE concept_id = %s""", (concept_id,))
        concept_name = cursor.fetchall()[0][0]
        d = {"subject": i[1],
             "description_attr": "Report",
             "source": "MIMIC Notes",
             "report_type": "test report",
             "report_text": i[5],
             "cg_id": "",
             "report_id": i[1],
             "is_error_attr": "",
             "id": i[1],
             "store_time_attr": "",
             "chart_time_attr": "",
             "admission_id": 123456,
             "report_date": str(i[11])
             }
        report_list.append(d)

    data = str(report_list)
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        reponse_message = "Successfully migrated data to Solr."
    else:
        reponse_message = "Could not upload. Contact Admin."

    conn.close()

    return reponse_message


def aact_db_upload(solr_url):
    conn_string = "host='%s' dbname='%s' user='%s' password='%s' port=%s" % ('aact-db.ctti-clinicaltrials.org',
                                                                             'aact',
                                                                             'aact',
                                                                             'aact',
                                                                             '5432')

    # Connecting to the AACT DB
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()

    # SOLR upload headers
    # url = solr_url + '/update/json'
    url = solr_url + '/update?commit=true'
    headers = {
        'Content-type': 'application/json',
    }

    # Extracting information - detailed_descriptions
    cursor.execute(
        """SELECT * FROM detailed_descriptions INNER JOIN studies ON studies.nct_id = detailed_descriptions.nct_id WHERE studies.first_received_date > '2018-01-01' LIMIT 1000""")
    result = cursor.fetchall()

    result_list = []
    for i in result:
        d = {"subject": i[1],
             "description_attr": "AACT Clinical Trials",
             "source": "AACT",
             "report_type": "Clinical Trial Description",
             "report_text": i[2],
             "cg_id": "",
             "report_id": i[0],
             "is_error_attr": "",
             "id": i[0],
             "store_time_attr": "",
             "chart_time_attr": "",
             "admission_id": "",
             "report_date": str(i[5])
             }

        result_list.append(d)

    # Pushing data to Solr
    data = json.dumps(result_list)
    response = requests.post(url, headers=headers, data=data)

    # Extracting information - Interventions
    cursor.execute(
        """SELECT * FROM interventions INNER JOIN studies ON studies.nct_id = interventions.nct_id WHERE studies.first_received_date > '2018-01-01' AND interventions.description IS NOT NULL LIMIT 1000 """)
    result = cursor.fetchall()

    result_list = []
    for i in result:
        d = {"subject": i[1],
             "description_attr": "AACT Clinical Trials",
             "source": "AACT",
             "report_type": "Clinical Trial Interventions",
             "report_text": str(i[4]),
             "cg_id": "",
             "report_id": i[0],
             "is_error_attr": "",
             "id": i[0],
             "store_time_attr": "",
             "chart_time_attr": "",
             "admission_id": "",
             "report_date": str(i[7])
             }

        result_list.append(d)

    # Pushing data to Solr
    data = json.dumps(result_list)
    response2 = requests.post(url, headers=headers, data=data)

    # Extracting information - Eligibilities
    cursor.execute(
        """SELECT eligibilities.id, eligibilities.nct_id, eligibilities.criteria, studies.first_received_date FROM eligibilities INNER JOIN studies ON studies.nct_id = eligibilities.nct_id WHERE studies.first_received_date > '2018-01-01' LIMIT 1000 """)
    result = cursor.fetchall()

    result_list = []
    for i in result:
        # Encoding as ASCII - Criteria field contains non ASCII characters
        report_text = i[2].encode('ascii', 'ignore')

        d = {"subject": i[1],
             "description_attr": "AACT Clinical Trials",
             "source": "AACT",
             "report_type": "Clinical Trial Criteria",
             "report_text": str(report_text),
             "cg_id": "",
             "report_id": i[0],
             "is_error_attr": "",
             "id": i[0],
             "store_time_attr": "",
             "chart_time_attr": "",
             "admission_id": "",
             "report_date": str(i[3])
             }

        result_list.append(d)

    # Pushing data to Solr
    data = json.dumps(result_list)
    response3 = requests.post(url, headers=headers, data=data)

    # Result verification
    if response.status_code == 200 and response2.status_code == 200 and response3.status_code == 200:
        response_msg = "Successfully migrated data to Solr."
    else:
        response_msg = "Could not upload. Contact Admin."

    print(response.status_code)
    print(response2.status_code)
    print(response3.status_code)
    conn.close()

    return response_msg


def upload_from_db(conn_string, solr_url, query):
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    report_list = []
    url = solr_url + '/update/json'
    headers = {
        'Content-type': 'application/json',
    }

    cursor.execute(query)
    result = cursor.fetchall()
    n = 0
    for i in result:
        d = {"report_id": i[0],
             "id": i[0],
             "subject": i[1],
             "source": i[2],
             "report_type": i[3],
             "report_date": str(i[4]),
             "report_text": i[5]
             }
        report_list.append(d)
        n += 1

    data = str(report_list)
    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        reponse_message = "Successfully migrated data to Solr."
    else:
        reponse_message = "Could not upload. Contact Admin."

    conn.close()

    return reponse_message


if __name__ == "__main__":
    print('local postgres upload')

    solr_url = 'http://localhost:8983/solr/sample'

    host = 'localhost'
    dbname = 'postgres'
    user = 'postgres'
    password = 'postgres'
    port = '5432'

    conn_string = "host='%s' dbname='%s' user='%s' password='%s' port=%s" % (host,
                                                                             dbname,
                                                                             user,
                                                                             password,
                                                                             port)
    query = ("""
        SELECT report_id, patient_id AS subject, 'My Test  Documents', report_type, report_date, report_text
            FROM
          mytable
        
        """)
    
    upload_from_db(conn_string, solr_url, query)
