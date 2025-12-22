from sqlalchemy.orm import Session
from ..models import Configuracao, Prompt, Funcao, CircuitBreakerState, RateLimit
from typing import List, Optional

class ConfigRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all_configs(self) -> List[Configuracao]:
        return self.db.query(Configuracao).all()

    def get_config_by_key(self, key: str) -> Optional[Configuracao]:
        return self.db.query(Configuracao).filter(Configuracao.chave == key).first()

    def create_config(self, key: str, value: str, tipo: str, category: str) -> Configuracao:
        config = Configuracao(chave=key, valor=value, tipo=tipo, categoria=category)
        self.db.add(config)
        self.db.commit()
        self.db.refresh(config)
        return config

    def update_config(self, id: int, updates: dict) -> Optional[Configuracao]:
        config = self.db.query(Configuracao).filter(Configuracao.id == id).first()
        if config:
            for k, v in updates.items():
                if v is not None:
                    setattr(config, k, v)
            self.db.commit()
            self.db.refresh(config)
        return config

    def delete_config(self, id: int) -> bool:
        config = self.db.query(Configuracao).filter(Configuracao.id == id).first()
        if config:
            self.db.delete(config)
            self.db.commit()
            return True
        return False

    # Prompts
    def get_prompts(self) -> List[Prompt]:
        return self.db.query(Prompt).all()

    def create_prompt(self, nome: str, template: str, versao: str) -> Prompt:
        prompt = Prompt(nome=nome, template=template, versao=versao)
        self.db.add(prompt)
        self.db.commit()
        self.db.refresh(prompt)
        return prompt

    def update_prompt(self, id: int, updates: dict) -> Optional[Prompt]:
        prompt = self.db.query(Prompt).filter(Prompt.id == id).first()
        if prompt:
            for k, v in updates.items():
                if v is not None:
                    setattr(prompt, k, v)
            self.db.commit()
            self.db.refresh(prompt)
        return prompt

    # Functions
    def get_functions(self) -> List[Funcao]:
        return self.db.query(Funcao).all()

    def create_function(self, nome: str, descricao: str, parameters: dict, tipo: str) -> Funcao:
        func = Funcao(nome=nome, descricao=descricao, parameters=parameters, tipo_tarefa=tipo)
        self.db.add(func)
        self.db.commit()
        self.db.refresh(func)
        return func

    # Circuit Breakers
    def get_circuit_breakers(self) -> List[CircuitBreakerState]:
        return self.db.query(CircuitBreakerState).all()

    def reset_circuit_breaker(self, id: int) -> Optional[CircuitBreakerState]:
        cb = self.db.query(CircuitBreakerState).filter(CircuitBreakerState.id == id).first()
        if cb:
            cb.state = 'closed'
            cb.failure_count = 0
            self.db.commit()
            self.db.refresh(cb)
        return cb

    # Rate Limits
    def get_rate_limits(self) -> List[RateLimit]:
        return self.db.query(RateLimit).all()

    def update_rate_limit(self, id: int, limit: int, interval: int) -> Optional[RateLimit]:
        rl = self.db.query(RateLimit).filter(RateLimit.id == id).first()
        if rl:
            rl.limit_count = limit
            rl.interval_seconds = interval
            self.db.commit()
            self.db.refresh(rl)
        return rl
