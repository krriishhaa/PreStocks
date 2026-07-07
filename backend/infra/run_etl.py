from backend.infra.pipeline import run_nightly_etl


if __name__ == "__main__":
    results = run_nightly_etl()
    for result in results:
        print(
            f"{result.pipeline_name}: {result.status} "
            f"(pulled={result.records_pulled}, valid={result.records_valid}, stored={result.records_stored})"
        )
        if result.errors:
            print(f"  errors={result.errors[:3]}")

