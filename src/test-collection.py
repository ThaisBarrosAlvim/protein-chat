import weaviate

weaviate_client = weaviate.connect_to_local()
collection = weaviate_client.collections.get("ProteinCollection")

count = 0
for item in collection.iterator():
    print(item.uuid, item.properties)
    count += 1
    if count > 3:
        break
weaviate_client.close()