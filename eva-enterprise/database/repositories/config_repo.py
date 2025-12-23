from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from ..models import Configuracao, Prompt, Funcao, CircuitBreakerState, RateLimit
from typing import List, Optional

class ConfigRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_configs(self) -> List[Configuracao]:
        query = select(Configuracao)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_config_by_key(self, key: str) -> Optional[Configuracao]:
        query = select(Configuracao).filter(Configuracao.chave == key)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_config(self, key: str, value: str, tipo: str, category: str) -> Configuracao:
        config = Configuracao(chave=key, valor=value, tipo=tipo, categoria=category)
        self.db.add(config)
        await self.db.commit()
        await self.db.refresh(config)
        return config

    async def update_config(self, id: int, updates: dict) -> Optional[Configuracao]:
        query = select(Configuracao).filter(Configuracao.id == id)
        result = await self.db.execute(query)
        config = result.scalar_one_or_none()
        if config:
            for k, v in updates.items():
                if v is not None:
                    setattr(config, k, v)
            await self.db.commit()
            await self.db.refresh(config)
        return config

    async def delete_config(self, id: int) -> bool:
        query = select(Configuracao).filter(Configuracao.id == id)
        result = await self.db.execute(query)
        config = result.scalar_one_or_none()
        if config:
            await self.db.delete(config)
            await self.db.commit()
            return True
        return False

    # Prompts
    async def get_prompts(self) -> List[Prompt]:
        query = select(Prompt)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_prompt(self, nome: str, template: str, versao: str) -> Prompt:
        prompt = Prompt(nome=nome, template=template, versao=versao)
        self.db.add(prompt)
        await self.db.commit()
        await self.db.refresh(prompt)
        return prompt

    async def update_prompt(self, id: int, updates: dict) -> Optional[Prompt]:
        query = select(Prompt).filter(Prompt.id == id)
        result = await self.db.execute(query)
        prompt = result.scalar_one_or_none()
        if prompt:
            for k, v in updates.items():
                if v is not None:
                    setattr(prompt, k, v)
            await self.db.commit()
            await self.db.refresh(prompt)
        return prompt

    # Functions
    async def get_functions(self) -> List[Funcao]:
        query = select(Funcao)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_function(self, nome: str, descricao: str, parameters: dict, tipo: str) -> Funcao:
        func = Funcao(nome=nome, descricao=descricao, parameters=parameters, tipo_tarefa=tipo)
        self.db.add(func)
        await self.db.commit()
        await self.db.refresh(func)
        return func

    # Circuit Breakers
    async def get_circuit_breakers(self) -> List[CircuitBreakerState]:
        query = select(CircuitBreakerState)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def reset_circuit_breaker(self, id: int) -> Optional[CircuitBreakerState]:
        query = select(CircuitBreakerState).filter(CircuitBreakerState.id == id)
        result = await self.db.execute(query)
        cb = result.scalar_one_or_none()
        if cb:
            cb.state = 'closed'
            cb.failure_count = 0
            await self.db.commit()
            await self.db.refresh(cb)
        return cb

    # Rate Limits
    async def get_rate_limits(self) -> List[RateLimit]:
        query = select(RateLimit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_rate_limit(self, id: int, limit: int, interval: int) -> Optional[RateLimit]:
        query = select(RateLimit).filter(RateLimit.id == id)
        result = await self.db.execute(query)
        rl = result.scalar_one_or_none()
        if rl:
            rl.limit_count = limit
            rl.interval_seconds = interval
            await self.db.commit()
            await self.db.refresh(rl)
        return rl
