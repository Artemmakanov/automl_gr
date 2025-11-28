import json
from llm.local_model import LocalLLM
from attacks.zero_shot import generate_zero_shot_attacks
from scoring.llm_scorer import llm_classifier
from hardening.summarize_attacks import summarize_patterns
from hardening.apply_to_system_prompt import build_hardened_prompt
from utils.metrics import compute_asr

def main():

    llm = LocalLLM()

    # 1. Load behaviors
    behaviors = json.load(open("data/behaviors.json"))
    
    # Optionally filter by semantic category
    behaviors = filter_behaviors(behaviors)

    # 2. Load original system prompt
    original_prompt = open("data/system_prompt.txt").read()

    # 3. Generate attacks
    attacks = generate_zero_shot_attacks(behaviors)

    # 4. FIRST RUN — evaluate attacks on original prompt
    results_before = []

    for atk in attacks:
        answer = llm.ask(original_prompt, atk["attack_prompt"])
        score = llm_classifier(llm, atk["behavior"], answer)

        results_before.append({
            "behavior": atk["behavior"],
            "attack_prompt": atk["attack_prompt"],
            "llm_answer": answer,
            "score": score
        })

    asr_before = compute_asr(results_before)
    print(f"ASR_before = {asr_before:.3f}")

    # 5. Collect successful ones
    successful = [x for x in results_before if x["score"] == 1]

    # 6. Summarize patterns → defensive rules
    defensive_rules = summarize_patterns(llm, successful)

    # 7. Create hardened system prompt
    hardened_prompt = build_hardened_prompt(original_prompt, defensive_rules)
    open("data/hardened_system_prompt.txt", "w").write(hardened_prompt)

    # 8. SECOND RUN — evaluate attacks on hardened prompt
    results_after = []

    for atk in attacks:
        answer = llm.ask(hardened_prompt, atk["attack_prompt"])
        score = llm_classifier(llm, atk["behavior"], answer)

        results_after.append({
            "behavior": atk["behavior"],
            "attack_prompt": atk["attack_prompt"],
            "llm_answer": answer,
            "score": score
        })

    asr_after = compute_asr(results_after)
    print(f"ASR_after = {asr_after:.3f}")

    print("Hardening improvement:", round(asr_before - asr_after, 3))


if __name__ == "__main__":
    main()
