import flask
from flask import request, jsonify
import fastjsonschema
import sqlite3

app = flask.Flask(__name__)
app.config["DEBUG"] = True

validate = fastjsonschema.compile({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "minItems": 1,
    "maxItems": 10,
    "items": {
        "type": "object",
        "properties": {
            "id": {"type": "integer"}
        },
        "required": ["id"]
    }
})

@app.errorhandler(fastjsonschema.exceptions.JsonSchemaException)
def handle_invalid_data(error):
    response = jsonify({"error": error.message})
    return response, 400

@app.route('/lab/instrument/<int:instrument_id>/samples', methods=['POST'])
def post_samples(instrument_id):
    payload = request.json
    samples = validate(payload)
    run_id = save(instrument_id, samples)
    return {"runId": run_id}

def save(instrument_id, samples):
    conn = sqlite3.connect('lab.db')
    c = conn.cursor()

    # Insert run
    c.execute('INSERT INTO run_instrument(instrument_id) VALUES (?)', (instrument_id,))

    # Retrieve run id
    c.execute('SELECT last_insert_rowid() AS id')
    run_id = c.fetchone()[0]

    # Insert samples belonging to run
    data = list(map(lambda x: (x["id"], run_id), samples))
    c.executemany('INSERT INTO run_sample(sample_id, run_id) VALUES (?, ?)', data)
	
    conn.commit()
    conn.close

    return run_id

app.run()