import weaviate

client = weaviate.connect_to_local()

try:
    result = client.backup.create(
        backup_id="protein-articles-semantic",
        backend="filesystem",
        include_collections=["ProteinCollectionSemantic",],
        wait_for_completion=True,
    )

    print(result)

finally:
    client.close()