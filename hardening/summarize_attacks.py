def summarize_patterns(llm, successful_attacks):

    sample = successful_attacks[:8]

    examples = "\n\n".join(
        f"Behavior: {x['behavior']}\nAttack: {x['attack_prompt']}\nAnswer: {x['llm_answer']}"
        for x in sample
    )

    system = "You are an LLM safety engineer."
    user = f"""
Here are successful jailbreak attempts:

{examples}

Extract general attack patterns and produce a concise list of defense rules 
that can be inserted into a system prompt.
"""

    return llm.ask(system, user)
