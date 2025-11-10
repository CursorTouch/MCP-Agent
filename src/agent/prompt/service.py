from importlib.resources import files
from src.agent.registry import Registry
from datetime import datetime
from typing import Any
import platform
import json

class Prompt:
    prompt_dir = files('src.agent.prompt')

    @staticmethod
    def system_prompt(max_steps:int,servers_info:list[dict[str,Any]],registry:Registry):
        prompt=Prompt.prompt_dir.joinpath('system.md').read_text()
        return prompt.format(**{
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'operating_system': platform.system(),
            'max_steps':max_steps,
            'servers_info': '\n'.join(map(lambda x: f'- {x["name"]}: {x["description"]} (Status: {"Connected" if x["status"] else "Disconnected"})', servers_info)),
            "tools":registry.get_tools_prompt(),
        })
    
    @staticmethod
    def action_prompt(thought:str,action_name:str,action_input:dict):
        prompt=Prompt.prompt_dir.joinpath('action.md').read_text()
        return prompt.format(**{
            "thought":thought,
            "action_name":action_name,
            "action_input":json.dumps(action_input,ensure_ascii=False),
        })

    @staticmethod
    def observation_prompt(steps:int,max_steps:int,observation:str):
        prompt=Prompt.prompt_dir.joinpath('observation.md').read_text()
        return prompt.format(**{
            "steps":steps,
            "max_steps":max_steps,
            "observation":observation,
        })

    @staticmethod
    def answer_prompt(thought:str,answer:str):
        prompt=Prompt.prompt_dir.joinpath('answer.md').read_text()
        return prompt.format(**{
            "thought":thought,
            "final_answer":answer,
        })
