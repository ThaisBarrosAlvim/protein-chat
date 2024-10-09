import weaviate

weaviate_client = weaviate.connect_to_local()
try:
    collection = weaviate_client.collections.get("ProteinCollectionSemantic")
    print('\n\nCollection: Collection: Collection: Collection: Collection: ', collection, '\n\n\n\n')
    print('ITEMS ITEMS ITEMS ITEMS ITEMS ITEMS ITEMS ITEMS ITEMS ITEMS ITEMS ')
    count = 0
    collections = weaviate_client.collections.list_all()
    for item in collection.iterator():
        print(item.uuid, item.properties)
        count += 1
        if count > 3:
            break
    print('\n\nFINISH FINISH FINISH FINISH FINISH FINISH FINISH FINISH ')
finally:
    weaviate_client.close()
