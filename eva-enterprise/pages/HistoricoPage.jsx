import React, { useState } from 'react';
import { History as HistoryIcon, PhoneCall, CheckCircle, XCircle, Heart, Search } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';

export default function HistoricoPage() {
    const { idosos } = useEva();
    const [searchTerm, setSearchTerm] = useState('');

    // Mock de histórico para visualização
    const historico = [
        { id: 1, idoso_nome: 'Maria Aparecida Silva', data: '2025-12-20 14:00', evento: 'Ligação Realizada', status: 'sucesso', detalhe: 'Tomou Losartana 50mg', sentimento: 'feliz' },
        { id: 2, idoso_nome: 'Carlos Eduardo Santos', data: '2025-12-20 10:30', evento: 'Ligação Realizada', status: 'alerta', detalhe: 'Relatou não ter o remédio em casa', sentimento: 'ansioso' },
        { id: 3, idoso_nome: 'Pedro Henrique Costa', data: '2025-12-19 15:45', evento: 'Tentativa de Ligação', status: 'falha', detalhe: 'Não atendeu após 3 tentativas', sentimento: '-' },
        { id: 4, idoso_nome: 'Rosa Maria Pereira', data: '2025-12-19 11:00', evento: 'Ligação Realizada', status: 'sucesso', detalhe: 'Confirmou medicação diária', sentimento: 'feliz' },
        { id: 5, idoso_nome: 'Maria Aparecida Silva', data: '2025-12-18 08:00', evento: 'Ligação Realizada', status: 'sucesso', detalhe: 'Confirmou café da manhã e remédio', sentimento: 'neutro' },
    ];

    const filteredHistorico = historico.filter(h =>
        h.idoso_nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
        h.evento.toLowerCase().includes(searchTerm.toLowerCase()) ||
        h.detalhe.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="p-8">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4 mb-6 bg-white p-6 rounded-2xl shadow-sm border border-pink-50">
                <h2 className="text-3xl font-bold text-pink-700 flex items-center gap-3 shrink-0">
                    <HistoryIcon className="w-8 h-8" />
                    Histórico
                </h2>
                <div className="flex-1 w-full relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Buscar por idoso, evento ou detalhe..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-100 rounded-2xl focus:outline-none focus:border-pink-400 transition-colors font-medium shadow-inner"
                    />
                </div>
            </div>

            <div className="bg-white rounded-2xl shadow-lg border border-pink-100 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-pink-50 text-pink-700 uppercase text-sm">
                        <tr>
                            <th className="px-6 py-4">Data/Hora</th>
                            <th className="px-6 py-4">Idoso</th>
                            <th className="px-6 py-4">Evento</th>
                            <th className="px-6 py-4">Status</th>
                            <th className="px-6 py-4">Humor Detectado</th>
                            <th className="px-6 py-4">Detalhes da EVA</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-pink-50">
                        {filteredHistorico.map(h => (
                            <tr key={h.id} className="hover:bg-pink-50/50 transition-colors">
                                <td className="px-6 py-4 text-gray-600 font-medium">{h.data}</td>
                                <td className="px-6 py-4 font-bold text-gray-800">{h.idoso_nome}</td>
                                <td className="px-6 py-4 text-gray-700">
                                    <span className="flex items-center gap-2">
                                        <PhoneCall className="w-4 h-4 text-pink-400" />
                                        {h.evento}
                                    </span>
                                </td>
                                <td className="px-6 py-4">
                                    {h.status === 'sucesso' && (
                                        <span className="flex items-center gap-1 text-green-600 bg-green-50 px-3 py-1 rounded-full text-xs font-bold w-fit">
                                            <CheckCircle className="w-3 h-3" /> CONCLUÍDO
                                        </span>
                                    )}
                                    {h.status === 'alerta' && (
                                        <span className="flex items-center gap-1 text-amber-600 bg-amber-50 px-3 py-1 rounded-full text-xs font-bold w-fit">
                                            <PhoneCall className="w-3 h-3" /> ATENÇÃO
                                        </span>
                                    )}
                                    {h.status === 'falha' && (
                                        <span className="flex items-center gap-1 text-red-600 bg-red-50 px-3 py-1 rounded-full text-xs font-bold w-fit">
                                            <XCircle className="w-3 h-3" /> FALHOU
                                        </span>
                                    )}
                                </td>
                                <td className="px-6 py-4">
                                    <div className="flex items-center gap-2">
                                        {h.sentimento === 'feliz' && <span className="text-green-600 bg-green-50 px-2 py-1 rounded-lg text-[10px] font-black uppercase">Feliz 😊</span>}
                                        {h.sentimento === 'neutro' && <span className="text-gray-600 bg-gray-50 px-2 py-1 rounded-lg text-[10px] font-black uppercase">Neutro 😐</span>}
                                        {h.sentimento === 'ansioso' && <span className="text-amber-600 bg-amber-50 px-2 py-1 rounded-lg text-[10px] font-black uppercase">Ansioso 😰</span>}
                                        {h.sentimento === '-' && <span className="text-gray-300">-</span>}
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-gray-600 text-sm italic">
                                    "{h.detalhe}"
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
