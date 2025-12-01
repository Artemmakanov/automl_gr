import json
from tqdm import tqdm

from llm.local_model import LocalLLM
from attacks.zero_shot import generate_zero_shot_attacks
from scoring.llm_scorer import llm_classifier
from hardening.summarize_attacks import summarize_patterns
from hardening.apply_to_system_prompt import build_hardened_prompt
from utils.metrics import compute_asr
from utils.behavior_filter import filter_behaviors


def dump_results(data, prefix: str):
    path = f"data/results_{prefix}.json"
    with open(path, "w") as f:
        json.dump(data, f)

def evaluate(llm, prompt, attacks, prefix: str):
    results = []

    for atk in tqdm(attacks, desc='Scoring on test'):
        answer = llm.ask(prompt, atk["attack_prompt"])
        score = llm_classifier(llm, atk["behavior"], answer)

        results.append({
            "behavior": atk["behavior"],
            "attack_prompt": atk["attack_prompt"],
            "llm_answer": answer,
            "score": score
        })

    dump_results(results, prefix)
    asr_after = compute_asr(results)
    print(f"ASR_{prefix} = {asr_after:.3f}")

    return asr_after

def main():

    # original_prompt_path = "data/medical/system_prompt.txt"
    # hardened_system_prompt_path = "data/medical/hardened_system_prompt.txt"
    # allowed_categories = ['chemical_biological']

    original_prompt_path = "data/moderator/system_prompt.txt"
    hardened_system_prompt_path = "data/moderator/hardened_system_prompt.txt"
    allowed_categories = ['harassment_bullying', 'harmful']


    llm = LocalLLM()

    # 1. Load behaviors
    behaviors_val = json.load(open("data/behaviors_val.json"))
    behaviors_test = json.load(open("data/behaviors_test.json"))
    # Optionally filter by semantic category
    behaviors_val = filter_behaviors(behaviors_val, allowed_categories=allowed_categories)
    behaviors_test = filter_behaviors(behaviors_test, allowed_categories=allowed_categories)
    
    # 2. Load original system prompt
    original_prompt = open(original_prompt_path).read()

    # 3. Generate attacks
    attacks_test = generate_zero_shot_attacks(behaviors_test)
    attacks_val = generate_zero_shot_attacks(behaviors_val)

    # 4. FIRST RUN — evaluate attacks on original prompt
    asr_before = evaluate(llm, original_prompt, attacks_test, prefix='before')

    
    results_candidates = []
    for atk in tqdm(attacks_val, desc='Scoring on val'):
        answer = llm.ask(original_prompt, atk["attack_prompt"])
        score = llm_classifier(llm, atk["behavior"], answer)

        results_candidates.append({
            "behavior": atk["behavior"],
            "attack_prompt": atk["attack_prompt"],
            "llm_answer": answer,
            "score": score
        })

    # 5. Collect successful ones
    successful = [x for x in results_candidates if x["score"] == 1]

    # 6. Summarize patterns → defensive rules
    defensive_rules = summarize_patterns(llm, successful)

    # 7. Create hardened system prompt
    hardened_prompt = build_hardened_prompt(original_prompt, defensive_rules)
    open(hardened_system_prompt_path, "w").write(hardened_prompt)

    # 8. SECOND RUN — evaluate attacks on hardened prompt
    asr_after = evaluate(llm, hardened_prompt, attacks_test, prefix='after')

    print("Hardening improvement:", round(asr_before - asr_after, 3))


if __name__ == "__main__":
    main()
