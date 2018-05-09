import csv
import configparser
import logging
import requests
import json
import copy
from no_ssl import no_ssl_verification

def wrap_sql(id,sql):
    wrapped = "SELECT * FROM ({sql}) as wrapped_query WHERE  <%= {layer_id} %> = 1".format(sql=sql,layer_id=id)
    return wrapped

def get_mod_name(template_name):
    return template_name + "_mod"

def modify_template(template):

    # Copy some objects
    layergroup = template['layergroup']
    input_layers = layergroup['layers']

    # Get the SQL qureies
    sources = {}
    for a in layergroup['analyses']:
        sources[a['id']] = a['params']['query']

    # For every cartodb layer
    layer_id_counter = 0

    for layer in input_layers:

        if layer['type'] == 'cartodb':
            layer_id = "layer{}".format(layer_id_counter)

            # Get the ID of the source
            options = layer['options']
            id = options['source']['id']

            # Change the SQL
            options['sql'] = wrap_sql(layer_id,sources[id])

            # Add a name with the same id
            options['layer_name'] = layer_id

            # Remove the external references
            del(options['source'])
            del(options['sql_wrap'])

            layer_id_counter = layer_id_counter + 1
    
    # Removing HTTP layers
    for layer in input_layers:
        if layer['type'] == 'http':
            input_layers.remove(layer)

    # Remove BUILDER objects
    del(layergroup['analyses'])
    del(layergroup['dataviews'])

    # Update the name
    template['name'] = get_mod_name(template['name'])

    return template



logging.basicConfig()
logger = logging.getLogger('namedmaps4js')
logger.setLevel(logging.DEBUG)

config = configparser.ConfigParser()
config.read("namedmaps4js.conf")

CARTO_BASE_URL = config.get('carto', 'base_url')
CARTO_API_KEY = config.get('carto', 'api_key')
MAP_LIST = config.get('carto','map_list')

with no_ssl_verification():
    with open(MAP_LIST, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            logger.info("Processing the map: {name} ({id})".format(name=row['name'],id=row['id']) )

            named_id = "tpl_" + row['id'].replace('-','_')

            # Get the input template
            url = "{url}api/v1/map/named/{template}?api_key={api}".format(
                url=CARTO_BASE_URL,
                template=named_id,
                api=CARTO_API_KEY)

            logger.info("Getting the named map template")
            request = requests.get(url)
            json_request = request.json()

            template = json_request['template']

            # Generate a new template
            logger.info("Modifying the template")
            output_template = modify_template(copy.deepcopy(template))

            # Check if the new template exists
            output_template_name = get_mod_name(named_id)
            url = "{url}api/v1/map/named/{template}?api_key={api}".format(
                url=CARTO_BASE_URL,
                template=output_template_name,
                api=CARTO_API_KEY)
            logger.info("Checking if the modified template exists...")
            r = requests.get(url)

            headers = {'Content-Type': 'application/json'}
            if r.status_code == 404:
                logger.info('Creating a new template')
                # New template
                url = "{url}api/v1/map/named?api_key={api}".format(
                    url=CARTO_BASE_URL,
                    api=CARTO_API_KEY)
                r = requests.post(url, headers = headers, data = json.dumps(output_template))
                if r.status_code == 200:
                    logger.info("OK!")
                else:
                    logger.warn("Something happened")
                    logger.warn(r.json())
            else:
                # Updated the template
                logger.info('Updating the template named')
                r = requests.put(url, headers = headers, data = json.dumps(output_template))
                if r.status_code == 200:
                    logger.info("OK!")
                else:
                    logger.warn("Something happened")
                    logger.warn(r.json())

            logger.info("Layer finished\r\n\r\n")

