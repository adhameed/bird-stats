# -*- coding: utf-8 -*-
"""
This flask app provides a very simple API for a web app to gather
several interesting datasets relating to the abundance of
the Australian Pied Oystercatcher, Haematopus longirostris
in Tasmanian waters.

It is a toy application intended for demonstration purposes only.
"""
import calendar  # english day names.
import logging  # make our life easier when debugging.
import os  # path joining.
from flask import Flask, jsonify, make_response
from flask_cors import CORS  # if someone loads the front end via file browser, localhost is CORS

DATA_DIR = 'data'
TOTALS_FILE = 'oys_totals.tsv'
FREQ_FILE = 'oys_freq.tsv'
"""
I'd much rather be using connexion (https://github.com/zalando/connexion) or blueprint
for loading API routes from an OpenAPI specification, but I ran out of time when putting
this brief demo together to do everything 'by the book'.
"""
APP = Flask(__name__)
CORS(APP)  # allow cross domain requests so the API doesn't get disallowed by the browser.


def get_tsv_dataset(dataset_path):
    """
    Helper function to get a single TSV row from a data file.
    :param dataset_path: str: path to a TSV that contains a one line dataset.
    :return: list of str, or None if data could not be read.
    """
    if not os.path.exists(dataset_path):
        logging.error('No such path %s', dataset_path)
        return None

    try:
        ds_file = open(dataset_path)
        data = ds_file.readline().strip().split('\t')
        return data
    except Exception:
        logging.error('Unexpected error getting data from %s', dataset_path, exc_info=True)

    # would have happened automatically, but explicit is always better than implicit
    return None


def make_simple_tsv_get_response(dataset_file, error_descriptor):
    """
    Given a filename and an error_descriptor, read a TSV file and
    return a jsonified response for use in a GET response.
    :param dataset_file: str: filename, with no fully qualified path.
    :param error_descriptor: str: the name of the data you were expecting to load, for logging.
    :return: a flask response object
    """
    try:
        data = get_tsv_dataset(os.path.join(DATA_DIR, dataset_file))
        if data is None:
            # something wrong with data.
            return make_response(jsonify({'error': 'Data could not be read'}), 500)

        # return the data + some pre-baked week  numbers to make plotting easier.
        # start plotting week at 1 since non-programmers prefer that.
        return jsonify({'labels': [x for x in range(1, len(data) + 1)],
                        'series': data})
    except Exception as err:
        # ideally we'd determine what errors can actually occur here.
        logging.error('Unexpected error getting %s data.', error_descriptor, exc_info=True)
        return make_response(jsonify({'error': 'Unexpected error: %s' % err}), 500)


def mean(a_series):
    """
    Calculate the arithmetic mean for 'a_series'.
    :param a_series: a series of ints or floats.
    :return: float: the arithmetic mean for this series.
    """
    return float(sum(a_series) / max(len(a_series) * 1.0, 1.0))


@APP.route('/corestats', methods=['GET'])
def core_stats():
    """
    Produce the a few basic statistics from the 'totals' dataset and return
    them to the user.
    :return: a JSONified object.
    """
    data = get_tsv_dataset(os.path.join(DATA_DIR, TOTALS_FILE))
    if data is None:
        return make_response(jsonify({'error': 'Data could not be read'}), 500)
    # parse up so we can manipulate things.
    dataset = [int(x) for x in data]
    annual_sightings = sum(dataset)
    # for each 'month' (selection of x4
    monthly_sightings = []
    max_sightings = 0
    max_month = 0

    # grab each month's data into its own list for post processing.
    # also calculate some other numbers as we go.
    for i in range(0, len(dataset), 4):
        # select 4x data points.
        this_month = dataset[i:i + 4]
        total_sightings_this_month = sum(this_month)
        monthly_sightings.append(total_sightings_this_month)
        old_max = max_sightings
        max_sightings = max(max_sightings, total_sightings_this_month)
        if old_max < max_sightings:
            # it could be the 0th month.
            max_month = len(monthly_sightings)

    mean_monthly_sightings = mean(monthly_sightings)
    month_name = list(calendar.month_name)[max_month]
    return make_response(jsonify({'annual_sightings': annual_sightings,
                                  'max_sightings': max_sightings,
                                  'max_sighting_month': month_name,
                                  'mean_monthly_sightings': mean_monthly_sightings}), 200)


@APP.route('/totals', methods=['GET'])
def totals():
    """
    Get totals observations for each week in the dataset.
    Explanation of totals: https://help.ebird.org/customer/portal/articles/1211517
    :return: a JSONified list of data.
    """
    return make_simple_tsv_get_response(TOTALS_FILE, 'totals')


@APP.route('/freq', methods=['GET'])
def frequency():
    """
    Read the species frequency from file and return it as json.
    Frequency should not be confused with basic number of sightings.
    A full explanation is shown here: https://help.ebird.org/customer/portal/articles/1210247
    :return: a JSONified list of data.
    """

    return make_simple_tsv_get_response(FREQ_FILE, 'frequency')


@APP.route('/')
def index():
    """
    Unused entry point of the API, could be removed.
    :return: str
    """
    return 'Thanks for using the Bird Stats API.'


if __name__ == '__main__':
    # attempt to find the data dir.
    if not os.path.exists(DATA_DIR):
        # Probably being run from inside the src dir. Proper code should check of course.
        logging.warning('Did not find the toplevel data dir, using ../data instead.')
        DATA_DIR = '../data'

    # Listen on all adaptors to make the sample more likely to run.
    APP.run(host='0.0.0.0', debug=True)
