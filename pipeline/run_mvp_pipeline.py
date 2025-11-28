from llm.local_model import LocalLLM
from attacks.zero_shot import generate_zero_shot_attacks
from scoring.llm_scorer import llm_classifier
from hardening.summarize_attacks import summarize_patterns
from hardening.apply_to_system_prompt import build_hardened_prompt
import json

from config import ALLOWED_BEHAVIOR_CATEGORIES

def filter_behaviors(behaviors):
    return [
        b for b in behaviors
        if b["category"] in ALLOWED_BEHAVIOR_CATEGORIES
    ]

def main():

    llm = LocalLLM()

    behaviors = json.load(open("data/behaviors.json"))
    behaviors = filter_behaviors(behaviors)

    original_prompt = open("data/system_prompt.txt").read()

    attacks = generate_zero_shot_attacks(behaviors)

    successful = []
    for atk in attacks:
        answer = llm.ask(original_prompt, atk["attack_prompt"])
        atk["llm_answer"] = answer
        score = llm_classifier(llm, atk["behavior"], answer)
        atk["score"] = score

        if score == 1:
            successful.append(atk)

    print(f"Found {len(successful)} successful attacks")

    rules = summarize_patterns(llm, successful)
    hardened = build_hardened_prompt(original_prompt, rules)

    open("data/hardened_system_prompt.txt", "w").write(hardened)

    print("Hardened system prompt saved.")


if __name__ == "__main__":
    main()
