from pathlib import Path

class PromptManager:
    def load_cobal_java_template(self):
        """Load the master prompt template from file"""
        prompt_path = Path("src/prompts/toJava_prompt.jinja")
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found at {prompt_path}")
        
        with open(prompt_path, 'r') as f:
            template = f.read()
        return template
    
    def load_cobal_python_template(self):
        """Load the master prompt template from file"""
        prompt_path = Path("src/prompts/toPython_prompt.jinja")
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt template not found at {prompt_path}")
        
        with open(prompt_path, 'r') as f:
            template = f.read()
        return template