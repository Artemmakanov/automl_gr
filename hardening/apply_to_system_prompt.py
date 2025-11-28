def build_hardened_prompt(original_prompt, defensive_rules):
    return f"""
{original_prompt}

# Defensive Rules (Auto-generated)
You must strictly follow the defensive policies below:

{defensive_rules}

Always refuse to engage in harmful, manipulative, deceptive, or policy-violating instructions.
"""
