import os
from gigachat import GigaChat
from typing import Literal, Optional
import asyncio
from dotenv import load_dotenv

async def get_description(description: str,user_adjustments: Optional[str] = None,) -> str:
    prompt = description
    if user_adjustments:
        prompt += f"\n\nУчти дополнительные правки: {user_adjustments}"
    load_dotenv()
    async with GigaChat(
        credentials=os.getenv("SECRET_KEY"),
        verify_ssl_certs=False,  
    ) as giga:
        response = await giga.achat(prompt)
        return response.choices[0].message.content

def descriptionCreator(name:str,about:str,target:Optional[str]="",hobby: Optional[str] = "", size:int=20):
    prompt = f"""Создай charismatic самопрезентацию для нетворкинга (до {size} предложений), используя данные ниже. 
                Стиль: живой, дружелюбный, без воды, с элементами харизмы. Добавь лёгкую неформальность, если уместно. Избегай шаблонов вроде «меня зовут… я занимаюсь…»,
                но обязательно используй все данные, которые я предоставлю. Но не додумывай и НЕ ПРИДУМЫВАЙ ФАКТЫ ИЗ ВОЗДУХА!
                Данные:

                Имя и особенности представления: {name}

                Деятельность (коротко и ярко): {about}

                Цель в нетворкинге: {target}

                Хобби/интересный факт: {hobby}"""
    return prompt
    
