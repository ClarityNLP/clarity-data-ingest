import glob
import json
import os
import uuid

in_path = '/Users/me/Downloads/'
out_path = '/Users/me/Downloads/out/'

if __name__ == "__main__":
    for filename in glob.glob(os.path.join(in_path, '*.json')):
        with open(filename) as j:
            name = filename.split('.')[0].split('/')[-1]
            data = json.load(j)

            solr_data_list = list()
            for doc in data:
                solr_data = {
                    "report_type": "Blog",
                    "report_id": str(uuid.uuid4()),
                    "source": "Nutrition Project",
                    "report_date": "1970-01-01T00:00:00Z",
                    "subject": name
                }

                if 'text' in doc and len(doc['text']) > 0:
                    txt = '\n '.join(doc['text'])
                    no_unicode_txt = txt.encode("ascii", errors="ignore").decode()
                    solr_data['report_text'] = no_unicode_txt

                    if 'tags' in doc:
                        solr_data['scraped_tags_attrs'] = doc['tags']

                    if 'date' in doc:
                        solr_data['scraped_date_attr'] = doc['date']

                    solr_data_list.append(solr_data)

            if len(solr_data_list) > 0:
                with open(os.path.join(out_path, name + '_out.json'), 'w') as outfile:
                    print(json.dumps(solr_data_list, indent=4))
                    json.dump(solr_data_list, outfile, indent=4)
