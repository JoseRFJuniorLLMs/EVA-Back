import React, { useState } from 'react';
import { X, Plus, Pill, Trash2, Clock, AlertCircle } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';

export default function MedicamentosModal({ isOpen, onClose, idoso }) {
    const { medicamentos, setMedicamentos } = useEva();
    const [isAdding, setIsAdding] = useState(false);

    // Form state
    const [novoMed, setNovoMed] = useState({
        nome: '',
        dosagem: '',
        forma: 'comprimido',
        horarios: '',
        observacoes: ''
    });

    if (!isOpen || !idoso) return null;

    const idosoMedicos = medicamentos.filter(m => m.idoso_id === idoso.id);

    const handleAdd = (e) => {
        e.preventDefault();
        const med = {
            id: Date.now(),
            idoso_id: idoso.id,
            ...novoMed,
            horarios: novoMed.horarios.split(',').map(h => h.trim())
        };
        setMedicamentos([...medicamentos, med]);
        setNovoMed({ nome: '', dosagem: '', forma: 'comprimido', horarios: '', observacoes: '' });
        setIsAdding(false);
    };

    const handleRemove = (id) => {
        setMedicamentos(medicamentos.filter(m => m.id !== id));
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[110] flex items-center justify-center p-4 animate-in fade-in duration-200">
            <div className="bg-white w-full max-w-2xl rounded-3xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
                {/* Header */}
                <div className="bg-gradient-to-r from-pink-600 to-purple-700 p-6 text-white flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-white/20 rounded-xl">
                            <Pill className="w-6 h-6" />
                        </div>
                        <div>
                            <h3 className="text-xl font-bold">Armário de Remédios</h3>
                            <p className="text-sm opacity-80">{idoso.nome}</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                <div className="p-6 max-h-[70vh] overflow-y-auto">
                    {!isAdding ? (
                        <div className="space-y-4">
                            <div className="flex justify-between items-center mb-6">
                                <h4 className="font-bold text-gray-700">Medicamentos Cadastrados</h4>
                                <button
                                    onClick={() => setIsAdding(true)}
                                    className="flex items-center gap-2 px-4 py-2 bg-pink-50 text-pink-600 rounded-xl font-bold hover:bg-pink-100 transition-colors"
                                >
                                    <Plus className="w-4 h-4" /> Adicionar
                                </button>
                            </div>

                            {idosoMedicos.length === 0 ? (
                                <div className="text-center py-12 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
                                    <Pill className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                                    <p className="text-gray-500">Nenhum medicamento cadastrado ainda.</p>
                                </div>
                            ) : (
                                idosoMedicos.map(med => (
                                    <div key={med.id} className="p-4 bg-gray-50 rounded-2xl border border-gray-100 flex justify-between items-start group hover:border-pink-200 transition-colors">
                                        <div className="flex gap-4">
                                            <div className="w-10 h-10 bg-white rounded-xl border border-gray-200 flex items-center justify-center text-pink-500">
                                                <Pill className="w-5 h-5" />
                                            </div>
                                            <div>
                                                <h5 className="font-bold text-gray-900">{med.nome} <span className="text-sm font-normal text-gray-500">({med.dosagem})</span></h5>
                                                <p className="text-xs text-gray-500 uppercase font-bold mt-1 tracking-wider">{med.forma}</p>

                                                <div className="flex flex-wrap gap-2 mt-3">
                                                    {med.horarios.map((h, i) => (
                                                        <span key={i} className="flex items-center gap-1 px-2 py-1 bg-white border border-gray-200 rounded-lg text-xs font-bold text-gray-600">
                                                            <Clock className="w-3 h-3 text-pink-400" /> {h}
                                                        </span>
                                                    ))}
                                                </div>
                                                {med.observacoes && (
                                                    <p className="text-sm text-gray-500 italic mt-3 flex items-center gap-1 leading-tight">
                                                        <AlertCircle className="w-3 h-3 text-amber-500 flex-shrink-0" />
                                                        {med.observacoes}
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => handleRemove(med.id)}
                                            className="p-2 text-gray-300 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all"
                                        >
                                            <Trash2 className="w-5 h-5" />
                                        </button>
                                    </div>
                                ))
                            )}
                        </div>
                    ) : (
                        <form onSubmit={handleAdd} className="space-y-4 animate-in slide-in-from-bottom-4 duration-300">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="col-span-2 sm:col-span-1">
                                    <label className="block text-sm font-bold text-gray-700 mb-1">Nome do Remédio</label>
                                    <input
                                        type="text" required
                                        className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-pink-500 outline-none"
                                        placeholder="Ex: Losartana"
                                        value={novoMed.nome}
                                        onChange={e => setNovoMed({ ...novoMed, nome: e.target.value })}
                                    />
                                </div>
                                <div className="col-span-2 sm:col-span-1">
                                    <label className="block text-sm font-bold text-gray-700 mb-1">Dosagem</label>
                                    <input
                                        type="text" required
                                        className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-pink-500 outline-none"
                                        placeholder="Ex: 50mg"
                                        value={novoMed.dosagem}
                                        onChange={e => setNovoMed({ ...novoMed, dosagem: e.target.value })}
                                    />
                                </div>
                                <div className="col-span-2 sm:col-span-1">
                                    <label className="block text-sm font-bold text-gray-700 mb-1">Forma</label>
                                    <select
                                        className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-pink-500 outline-none"
                                        value={novoMed.forma}
                                        onChange={e => setNovoMed({ ...novoMed, forma: e.target.value })}
                                    >
                                        <option value="comprimido">Comprimido</option>
                                        <option value="capsula">Cápsula</option>
                                        <option value="liquido">Líquido (Xarope/Gota)</option>
                                        <option value="injetavel">Injetável</option>
                                        <option value="pomada">Pomada/Creme</option>
                                    </select>
                                </div>
                                <div className="col-span-2 sm:col-span-1">
                                    <label className="block text-sm font-bold text-gray-700 mb-1">Horários (separados por vírgula)</label>
                                    <input
                                        type="text" required
                                        className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-pink-500 outline-none"
                                        placeholder="Ex: 08:00, 20:00"
                                        value={novoMed.horarios}
                                        onChange={e => setNovoMed({ ...novoMed, horarios: e.target.value })}
                                    />
                                </div>
                                <div className="col-span-2">
                                    <label className="block text-sm font-bold text-gray-700 mb-1">Observações da EVA</label>
                                    <textarea
                                        rows="2"
                                        className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-pink-500 outline-none"
                                        placeholder="O que a EVA deve falar ao idoso? (Ex: Tomar após o almoço)"
                                        value={novoMed.observacoes}
                                        onChange={e => setNovoMed({ ...novoMed, observacoes: e.target.value })}
                                    />
                                </div>
                            </div>

                            <div className="flex gap-4 pt-4 border-t">
                                <button
                                    type="button"
                                    onClick={() => setIsAdding(false)}
                                    className="flex-1 py-3 px-6 bg-gray-100 text-gray-600 rounded-xl font-bold hover:bg-gray-200 transition-colors"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    className="flex-1 py-3 px-6 bg-pink-600 text-white rounded-xl font-bold hover:bg-pink-700 shadow-lg shadow-pink-200 transition-colors"
                                >
                                    Salvar Medicamento
                                </button>
                            </div>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
}
