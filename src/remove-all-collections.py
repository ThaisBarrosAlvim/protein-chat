import weaviate

weaviate_client = weaviate.connect_to_local(host='weaviate')
weaviate_client.connect()
weaviate_client.collections.delete_all()
weaviate_client.close()