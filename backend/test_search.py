from db_manager import DatabaseManager

db = DatabaseManager()
results = db.search("Főzős kisfőnök feladata", top_k=2)

for idx, match in enumerate(results, start=1):
    print(f"\n--- Match #{idx} ---")
    print(f"Content: {match['text']}")
    print(f"Metadata Source: {match['metadata']}")
