"""
Load Test Suite - Eva Enterprise
Simula múltiplas chamadas simultâneas para teste de carga
"""
import asyncio
import aiohttp
import argparse
import statistics
import random
from datetime import datetime
from typing import List, Dict, Optional


class LoadTester:
    """Simula múltiplas chamadas simultâneas."""
    
    def __init__(self, base_url: str, max_concurrent: int = 10):
        self.base_url = base_url.rstrip('/')
        self.max_concurrent = max_concurrent
        self.results: List[Dict] = []
        self.errors: List[Dict] = []
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def simulate_call(self, agendamento_id: int) -> dict:
        """Simula uma chamada completa"""
        async with self.semaphore:  # Limita concorrência
            start_time = datetime.utcnow()
            
            try:
                async with aiohttp.ClientSession() as session:
                    # Inicia chamada
                    async with session.post(
                        f"{self.base_url}/make-call",
                        params={'agendamento_id': agendamento_id},
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as resp:
                        if resp.status != 200:
                            raise Exception(f"HTTP {resp.status}")
                        
                        call_data = await resp.json()
                    
                    # Simula duração da chamada
                    call_duration = random.uniform(30, 60)
                    await asyncio.sleep(call_duration)
                    
                    end_time = datetime.utcnow()
                    duration = (end_time - start_time).total_seconds()
                    
                    result = {
                        'agendamento_id': agendamento_id,
                        'success': True,
                        'duration_seconds': duration,
                        'call_sid': call_data.get('call_sid'),
                        'timestamp': start_time.isoformat()
                    }
                    
                    self.results.append(result)
                    print(f"✓ Chamada #{agendamento_id} concluída ({duration:.1f}s)")
                    return result
            
            except asyncio.TimeoutError:
                error = self._create_error(agendamento_id, start_time, "Timeout")
                self.errors.append(error)
                return error
            
            except Exception as e:
                error = self._create_error(agendamento_id, start_time, str(e))
                self.errors.append(error)
                return error
    
    def _create_error(self, agendamento_id: int, start_time: datetime, error_msg: str) -> dict:
        """Cria registro de erro"""
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        error = {
            'agendamento_id': agendamento_id,
            'success': False,
            'duration_seconds': duration,
            'error': error_msg,
            'timestamp': start_time.isoformat()
        }
        
        print(f"✗ Chamada #{agendamento_id} falhou: {error_msg}")
        return error
    
    async def run_load_test(
        self, 
        num_calls: int, 
        ramp_up_seconds: int = 10,
        randomize_delay: bool = True
    ):
        """
        Executa teste de carga.
        
        Args:
            num_calls: Número total de chamadas
            ramp_up_seconds: Tempo para iniciar todas as chamadas
            randomize_delay: Se True, adiciona variação no delay
        """
        print("\n" + "="*60)
        print("🚀 LOAD TEST - EVA ENTERPRISE")
        print("="*60)
        print(f"URL Base: {self.base_url}")
        print(f"Chamadas: {num_calls}")
        print(f"Ramp-up: {ramp_up_seconds}s")
        print(f"Concorrência máxima: {self.max_concurrent}")
        print("="*60 + "\n")
        
        delay_between_calls = ramp_up_seconds / num_calls
        
        tasks = []
        for i in range(num_calls):
            task = asyncio.create_task(self.simulate_call(agendamento_id=i + 1))
            tasks.append(task)
            
            # Delay com variação opcional
            delay = delay_between_calls
            if randomize_delay:
                delay *= random.uniform(0.5, 1.5)
            
            await asyncio.sleep(delay)
        
        print(f"\n⏳ Aguardando conclusão de {num_calls} chamadas...")
        await asyncio.gather(*tasks, return_exceptions=True)
        
        self._print_report()
    
    def _print_report(self):
        """Imprime relatório de resultados"""
        total = len(self.results) + len(self.errors)
        success_count = len(self.results)
        error_count = len(self.errors)
        
        success_rate = (success_count / total * 100) if total > 0 else 0
        error_rate = (error_count / total * 100) if total > 0 else 0
        
        print("\n" + "="*60)
        print("📊 RELATÓRIO DE LOAD TEST")
        print("="*60)
        print(f"Total de chamadas: {total}")
        print(f"✓ Sucessos: {success_count} ({success_rate:.1f}%)")
        print(f"✗ Erros: {error_count} ({error_rate:.1f}%)")
        
        if self.results:
            durations = [r['duration_seconds'] for r in self.results]
            p95_idx = min(int(len(durations) * 0.95), len(durations) - 1)
            
            print(f"\n⏱️ Duração das chamadas:")
            print(f"  - Média:   {statistics.mean(durations):.2f}s")
            print(f"  - Mediana: {statistics.median(durations):.2f}s")
            print(f"  - Min:     {min(durations):.2f}s")
            print(f"  - Max:     {max(durations):.2f}s")
            print(f"  - P95:     {sorted(durations)[p95_idx]:.2f}s")
            
            if len(durations) > 1:
                print(f"  - StdDev:  {statistics.stdev(durations):.2f}s")
        
        if self.errors:
            print(f"\n❌ Erros encontrados:")
            error_types = {}
            for error in self.errors:
                error_msg = error['error']
                error_types[error_msg] = error_types.get(error_msg, 0) + 1
            
            for error_msg, count in sorted(error_types.items(), key=lambda x: -x[1]):
                print(f"  - {error_msg}: {count} ocorrências")
        
        # Throughput
        if self.results:
            first_start = min(datetime.fromisoformat(r['timestamp']) for r in self.results)
            last_end = datetime.utcnow()
            total_time = (last_end - first_start).total_seconds()
            throughput = success_count / total_time if total_time > 0 else 0
            print(f"\n📈 Throughput: {throughput:.2f} chamadas/segundo")
        
        print("="*60)
        
        # Retorna métricas para uso programático
        return {
            'total': total,
            'success_count': success_count,
            'error_count': error_count,
            'success_rate': success_rate,
            'durations': [r['duration_seconds'] for r in self.results] if self.results else []
        }


class WebSocketLoadTester:
    """Testa conexões WebSocket simultâneas."""
    
    def __init__(self, ws_url: str, max_concurrent: int = 10):
        self.ws_url = ws_url
        self.max_concurrent = max_concurrent
        self.connections_established = 0
        self.connection_errors = 0
        self.messages_received = 0
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def test_websocket(self, duration_seconds: int = 30) -> dict:
        """Testa uma conexão WebSocket"""
        async with self.semaphore:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.ws_connect(self.ws_url) as ws:
                        self.connections_established += 1
                        print(f"✓ WebSocket #{self.connections_established} conectado")
                        
                        # Mantém conexão aberta por X segundos
                        start = datetime.utcnow()
                        while (datetime.utcnow() - start).total_seconds() < duration_seconds:
                            try:
                                msg = await asyncio.wait_for(ws.receive(), timeout=1.0)
                                if msg.type == aiohttp.WSMsgType.TEXT:
                                    self.messages_received += 1
                                elif msg.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                                    break
                            except asyncio.TimeoutError:
                                pass
                        
                        return {'success': True}
            
            except Exception as e:
                self.connection_errors += 1
                return {'success': False, 'error': str(e)}
    
    async def run_websocket_test(self, num_connections: int, duration_seconds: int = 30):
        """Executa teste de conexões WebSocket"""
        print(f"🔌 Testando {num_connections} conexões WebSocket por {duration_seconds}s...")
        
        tasks = [
            asyncio.create_task(self.test_websocket(duration_seconds))
            for _ in range(num_connections)
        ]
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        print(f"\n📊 Resultados WebSocket:")
        print(f"  - Conexões estabelecidas: {self.connections_established}")
        print(f"  - Erros de conexão: {self.connection_errors}")
        print(f"  - Mensagens recebidas: {self.messages_received}")


async def run_stress_test(base_url: str, duration_minutes: int = 5):
    """Teste de estresse contínuo"""
    print(f"🔥 Iniciando stress test por {duration_minutes} minutos...")
    
    tester = LoadTester(base_url, max_concurrent=20)
    
    start = datetime.utcnow()
    call_id = 0
    
    while (datetime.utcnow() - start).total_seconds() < duration_minutes * 60:
        call_id += 1
        asyncio.create_task(tester.simulate_call(call_id))
        await asyncio.sleep(random.uniform(1, 5))  # 1-5s entre chamadas
    
    # Aguarda chamadas em andamento
    await asyncio.sleep(60)
    
    tester._print_report()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Load test para Eva Enterprise')
    parser.add_argument('--url', required=True, help='URL base da API')
    parser.add_argument('--calls', type=int, default=50, help='Número de chamadas')
    parser.add_argument('--ramp-up', type=int, default=30, help='Ramp-up em segundos')
    parser.add_argument('--concurrent', type=int, default=10, help='Máx. concorrência')
    parser.add_argument('--mode', choices=['load', 'stress', 'websocket'], default='load',
                        help='Modo de teste')
    parser.add_argument('--duration', type=int, default=5, help='Duração stress test (min)')
    
    args = parser.parse_args()
    
    if args.mode == 'load':
        tester = LoadTester(base_url=args.url, max_concurrent=args.concurrent)
        asyncio.run(tester.run_load_test(args.calls, args.ramp_up))
    
    elif args.mode == 'stress':
        asyncio.run(run_stress_test(args.url, args.duration))
    
    elif args.mode == 'websocket':
        ws_url = args.url.replace('http', 'ws') + '/media-stream'
        tester = WebSocketLoadTester(ws_url, max_concurrent=args.concurrent)
        asyncio.run(tester.run_websocket_test(args.calls, args.duration * 60))
