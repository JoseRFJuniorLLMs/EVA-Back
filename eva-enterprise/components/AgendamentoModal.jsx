import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';

export default function AgendamentoModal({ isOpen, onClose, agendamentoToEdit = null, preSelectedIdosoId = '' }) {
    const { idosos, carregarDashboard } = useEva();

    const [formAgendamento, setFormAgendamento] = useState({
        idoso_id: '', horario: '', remedios: '', repetir: 'nao'
    });

    useEffect(() => {
        if (agendamentoToEdit) {
            setFormAgendamento(agendamentoToEdit);
        } else {
            setFormAgendamento({
                idoso_id: preSelectedIdosoId || '',
                horario: '',
                remedios: '',
                repetir: 'nao'
            });
        }
    }, [agendamentoToEdit, isOpen, preSelectedIdosoId]);

    const salvarAgendamento = () => {
        console.log('Salvando agendamento:', formAgendamento);
        carregarDashboard();
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-screen overflow-y-auto border border-pink-200">
                <div className="p-8">
                    <div className="flex justify-between items-center mb-8">
                        <h3 className="text-2xl font-bold text-pink-700">
                            {agendamentoToEdit ? 'Editar Agendamento' : 'Novo Agendamento'}
                        </h3>
                        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                            <X className="w-8 h-8" />
                        </button>
                    </div>

                    <div className="space-y-6">
                        <div>
                            <label className="block text-lg font-medium mb-2">Idoso</label>
                            <select value={formAgendamento.idoso_id} onChange={e => setFormAgendamento({ ...formAgendamento, idoso_id: e.target.value })} className="w-full px-5 py-3 text-lg border-2 border-pink-200 rounded-xl focus:border-pink-500 focus:ring-4 focus:ring-pink-100">
                                <option value="">Selecione o idoso</option>
                                {(idosos || []).map(idoso => (
                                    <option key={idoso.id} value={idoso.id}>{idoso.nome} - {idoso.telefone}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label className="block text-lg font-medium mb-2">Data e Hora da Ligação</label>
                            <input type="datetime-local" value={formAgendamento.horario} onChange={e => setFormAgendamento({ ...formAgendamento, horario: e.target.value })} className="w-full px-5 py-3 text-lg border-2 border-pink-200 rounded-xl focus:border-pink-500 focus:ring-4 focus:ring-pink-100" />
                        </div>
                        <div>
                            <label className="block text-lg font-medium mb-2">Remédios e Instruções</label>
                            <textarea placeholder="Ex: Tomar Losartana 50mg às 14h, confirmar se tomou o remédio do coração..." value={formAgendamento.remedios} onChange={e => setFormAgendamento({ ...formAgendamento, remedios: e.target.value })} className="w-full px-5 py-3 text-lg border-2 border-pink-200 rounded-xl focus:border-pink-500 focus:ring-4 focus:ring-pink-100" rows="6" />
                        </div>
                        <button onClick={salvarAgendamento} className="w-full py-4 bg-gradient-to-r from-pink-600 to-purple-600 text-white rounded-xl hover:from-pink-700 hover:to-purple-700 font-bold text-xl shadow-lg">
                            Agendar Ligação Automática
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
