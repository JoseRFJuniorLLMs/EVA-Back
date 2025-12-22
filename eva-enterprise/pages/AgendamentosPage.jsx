import React, { useState } from 'react';
import { CalendarPlus, PhoneCall, Search } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';
import AgendamentoModal from '../components/AgendamentoModal';
import { toast } from 'sonner';

export default function AgendamentosPage() {
    const { agendamentos, carregarDashboard, idosos, dispararChamadaImediata } = useEva();
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const [callingId, setCallingId] = useState(null);

    const filteredAgendamentos = (agendamentos || []).filter(ag =>
        (ag.idoso_nome || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
        (ag.remedios || '').toLowerCase().includes(searchTerm.toLowerCase())
    );

    const dispararLigacaoManual = async (agendamento) => {
        try {
            setCallingId(agendamento.id);
            const idoso = idosos.find(i => i.nome === agendamento.idoso_nome);
            await dispararChamadaImediata(idoso || { nome: agendamento.idoso_nome });
            setCallingId(null);
            toast.success(`Ligação iniciada para ${agendamento.idoso_nome}`);
            carregarDashboard();
        } catch (error) {
            setCallingId(null);
            toast.error('Erro de conexão ao tentar ligar');
        }
    };

    return (
        <div className="p-8">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4 mb-8 bg-white p-6 rounded-2xl shadow-sm border border-pink-50">
                <div className="flex-1 w-full relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Buscar por idoso ou remédios..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-100 rounded-2xl focus:outline-none focus:border-pink-400 transition-colors font-medium shadow-inner"
                    />
                </div>
                <button onClick={() => setIsModalOpen(true)} className="flex items-center gap-3 px-8 py-3 bg-pink-600 text-white rounded-2xl hover:bg-pink-700 shadow-lg shadow-pink-200 font-bold transition-all shrink-0">
                    <CalendarPlus className="w-6 h-6" />
                    Novo Agendamento
                </button>
            </div>

            <div className="bg-white rounded-2xl shadow-lg border border-pink-100 overflow-hidden">
                <table className="w-full">
                    <thead className="bg-pink-100">
                        <tr>
                            <th className="px-6 py-4 text-left text-sm font-semibold text-pink-800">Idoso</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold text-pink-800">Horário</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold text-pink-800">Remédios</th>
                            <th className="px-6 py-4 text-left text-sm font-semibold text-pink-800">Status</th>
                            <th className="px-6 py-4 text-right text-sm font-semibold text-pink-800">Ações</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-pink-100">
                        {filteredAgendamentos.map(ag => (
                            <tr key={ag.id} className="hover:bg-pink-50 transition-colors">
                                <td className="px-6 py-4 font-medium">{ag.idoso_nome}</td>
                                <td className="px-6 py-4">{ag.horario}</td>
                                <td className="px-6 py-4">{ag.remedios}</td>
                                <td className="px-6 py-4">
                                    <span className={`px-4 py-2 text-sm rounded-full font-medium ${ag.status === 'pendente' ? 'bg-yellow-100 text-yellow-800' :
                                        ag.status === 'em_andamento' ? 'bg-pink-100 text-pink-800' :
                                            ag.status === 'concluido' ? 'bg-green-100 text-green-800' :
                                                'bg-red-100 text-red-800'
                                        }`}>
                                        {ag.status}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-right">
                                    {ag.status === 'pendente' && (
                                        <button
                                            onClick={() => dispararLigacaoManual(ag)}
                                            className={`${callingId === ag.id ? 'text-green-600 animate-pulse' : 'text-pink-600 hover:text-green-600'} font-medium transition-colors`}
                                            disabled={callingId !== null}
                                        >
                                            <PhoneCall className="w-5 h-5 inline mr-1" /> {callingId === ag.id ? 'Chamando...' : 'Ligar Agora'}
                                        </button>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <AgendamentoModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
            />
        </div>
    );
}
