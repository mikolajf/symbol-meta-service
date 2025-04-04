import argparse
import json

from app.main import app

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate OpenAPI schema")
    parser.add_argument(
        "--output", type=str, default="openapi_schema.json", help="Output file path"
    )
    args = parser.parse_args()

    # get openapi schema from app object
    schema = app.openapi()

    with open(args.output, "w") as f:
        json.dump(schema, f)
