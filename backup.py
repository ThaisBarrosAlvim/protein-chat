import weaviate

client = weaviate.connect_to_local()

try:
    result = client.backup.create(
        backup_id="protein-articles4",
        backend="filesystem",
        include_collections=["ProteinCollection",],
        wait_for_completion=True,
    )

    print(result)

finally:
    client.close()