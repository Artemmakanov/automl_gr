from llama_cpp import Llama

class LocalLLM:
    def __init__(self, model_path="models/llama32-3b-instruct-q4.gguf"):
        self.llm = Llama(
            model_path=model_path,
            n_ctx=4096,
            n_gpu_layers=50,     # часть слоёв пускаем на GPU
            n_batch=512,
            verbose=False
        )

    def ask(self, system_prompt, user_prompt):
        prompt = f"<|begin_of_text|><system>{system_prompt}</system><user>{user_prompt}</user><assistant>"
        out = self.llm(prompt, max_tokens=256, temperature=0.0)
        return out["choices"][0]["text"].strip()
