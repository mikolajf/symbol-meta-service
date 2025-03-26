import json


from app.main import app

if __name__ == "__main__":
    # get openapi schema from app object
    schema = app.openapi()

    json.dump(schema, open("openapi_schema.json", "w"))
