from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from schema import schema_donut
from exceptions import InvalidSchemaError, InvalidValue
from http import HTTPStatus
from subprocess import Popen
import helper
import sqlite3


# todo: test schema
# todo: test code

app = Flask(__name__)
api = Api(app)


class Donuts(Resource):
    """ Donuts factory class. """
    def post(self):
        # ! data is list
        data = request.get_json()
        for dictionary in data:
            try:
                helper.validate_schema(schema_donut, dictionary)
            except InvalidSchemaError as ex:
                return jsonify({"message": ex.args[0], "code": ex.args[1]})

        try:
            result_data = helper.generate_all_data(data)
        except InvalidValue as ex:
            return jsonify({"message": ex.args[0], "code": ex.args[1]})
        connection = sqlite3.connect("data.db")
        cursor = connection.cursor()
        create_table = """
        CREATE TABLE IF NOT EXISTS donuts (
            id text, type text, name text, batters text, toppings text
        )
        """
        cursor.execute(create_table)
        insert_query = "INSERT INTO donuts VALUES (?, ?, ?, ?, ?)"
        cursor.executemany(insert_query, result_data)

        return jsonify(
            {
                "message": "data saved into database",
                "code": HTTPStatus.OK
            }
        )


api.add_resource(Donuts, "/donuts")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
