import weaviate
import json


def main():
    auth_config = weaviate.AuthApiKey(api_key="readonly-demo")  # Replace w/ your Weaviate API key

    # Instantiate the client
    client = weaviate.Client(
        url="http://localhost:8080",  # Replace with your sandbox URL
        # auth_client_secret=auth_config,
    )

    print(json.dumps(client.get_meta(), indent=2))
    print(json.dumps(client.schema.get(), indent=2))


if __name__ == "__main__":
    main()

