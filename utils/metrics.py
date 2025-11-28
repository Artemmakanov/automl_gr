def compute_asr(results):
    if not results:
        return 0.0
    successes = sum(r["score"] for r in results)
    return successes / len(results)
