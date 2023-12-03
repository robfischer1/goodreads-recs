import json
import logging
import sqlite3
from pprint import pprint

import pandas as pd
import tensorflow as tf

pd.set_option('display.width', 400)
pd.set_option('display.max_columns', 7)

example_data = {
    # 'context_id': [9, 31, 34],
    # 'context_rating': [5.0, 4.0, 5.0]
    'context_id': [9],
    'context_rating': [5.0]
}

example_request = json.dumps(example_data)


def parse_request(json_req):
    query = json.loads(json_req)
    for k, v in query.items():
        query[k] += [0] * (10 - len(v))
    return query


def get_predictions(query):
    model = tf.saved_model.load('model_dir/export')
    # query = {k: tf.convert_to_tensor(v) for k, v in query.items()}
    recommendations = model.serve(**query)
    predictions = [int(v) for v in recommendations['recommendation_ids'].numpy()]
    return predictions


def _row_to_json(cursor, row):
    fields = [column[0] for column in cursor.description]
    return json.dumps({key: value for key, value in zip(fields, row)})


def get_page(conn, page_no=1, page_size=25):
    start_from = 1 + (page_no - 1) * page_size
    cols = "work_index, title, author_name, average_rating, link, image_url"
    page = conn.execute(f"SELECT {cols} FROM books WHERE work_index >= ? LIMIT ?", (start_from, page_size))
    return page.fetchall()


def get_results(conn, predictions, limit=10):
    cols = "work_index, title, author_name, average_rating, link, image_url"
    query = f"SELECT {cols} FROM books WHERE work_index IN ({','.join(['?']*limit)})"
    results = conn.execute(query, tuple(predictions[:limit]))
    return results.fetchall()


"""con = sqlite3.connect("../data/app.db")
con.row_factory = _row_to_json

example_query = parse_request(example_request)
example_predictions = get_predictions(example_query)
example_recs = list(set(example_predictions) - set(example_query['context_id']))
example_results = get_results(con, example_recs)

for result in example_results:
    print(json.loads(result)['title'])"""

con = sqlite3.connect("../data/app.db")
results = con.execute("SELECT * from books WHERE image_url LIKE '%nophoto%'")
print(len(results.fetchall()))