import flask
from flask import request, jsonify
import fastjsonschema

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
    print(error)
    response = jsonify({"error": error.message})
    return response, 400

@app.route('/lab/instrument/<int:instrument_id>/samples', methods=['POST'])
def post_samples(instrument_id):
    payload = request.json
    samples = validate(payload)
    print(samples)
    run = {"runId": 1}
    return run

app.run()