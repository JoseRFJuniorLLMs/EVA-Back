import React, { useState } from 'react';
import { X, Plus, Users, Trash2, Phone, ShieldAlert, MessageSquare } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';

export default function EquipeCuidadoModal({ isOpen, onClose, idoso }) {
    const { contatosAlerta, setContatosAlerta } = useEva();
    const [isAdding, setIsAdding] = useState(false);

    // Form state
    const [novoContato, setNovoContato] = useState({
        nome: '',
        telefone: '',
        parentesco: '',
        prioritario: false,
        canais: ['SMS']
    });

    if (!isOpen || !idoso) return null;

    const contatosIdoso = contatosAlerta.filter(c => c.idoso_id === idoso.id);

    const handleAdd = (e) => {
        e.preventDefault();
        const contato = {
            id: Date.now(),
            idoso_id: idoso.id,
            ...novoContato
        };
        setContatosAlerta([...contatosAlerta, contato]);
        setNovoContato({ nome: '', telefone: '', parentesco: '', prioritario: false, canais: ['SMS'] });
        setIsAdding(false);
    };

    const handleRemove = (id) => {
        setContatosAlerta(contatosAlerta.filter(c => c.id !== id));
    };

    const toggleCanal = (canal) => {
        const canais = novoContato.canais.includes(canal)
            ? novoContato.canais.filter(c => c !== canal)
            : [...novoContato.canais, canal];
        setNovoContato({ ...novoContato, canais });
    };

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[110] flex items-center justify-center p-4 animate-in fade-in duration-200">
            <div className="bg-white w-full max-w-2xl rounded-3xl shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
                {/* Header */}
                <div className="bg-gradient-to-r from-blue-600 to-indigo-700 p-5 text-white flex justify-between items-center">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-white/20 rounded-xl">
                            <Users className="w-5 h-5" />
                        </div>
                        <div>
                            <h3 className="text-lg font-bold">Equipe de Cuidado</h3>
                            <p className="text-sm opacity-80">Gestão de contatos para: {idoso.nome}</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-colors">
                        <X className="w-5 h-5" />
                    </button>
                </div>

                <div className="p-5 max-h-[70vh] overflow-y-auto">
                    {!isAdding ? (
                        <div className="space-y-4">
                            <div className="flex justify-between items-center mb-4">
                                <h4 className="font-bold text-gray-700">Contatos de Notificação</h4>
                                <button
                                    onClick={() => setIsAdding(true)}
                                    className="flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-600 rounded-xl font-bold hover:bg-blue-100 transition-colors"
                                >
                                    <Plus className="w-4 h-4" /> Adicionar
                                </button>
                            </div>

                            {contatosIdoso.length === 0 ? (
                                <div className="text-center py-12 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200">
                                    <Users className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                                    <p className="text-gray-500">Nenhum contato cadastrado.</p>
                                </div>
                            ) : (
                                contatosIdoso.map(contato => (
                                    <div key={contato.id} className="p-4 bg-gray-50 rounded-2xl border border-gray-100 flex justify-between items-center group hover:border-blue-200 transition-colors">
                                        <div className="flex gap-4">
                                            <div className={`w-10 h-10 rounded-xl border flex items-center justify-center ${contato.prioritario ? 'bg-red-50 border-red-100 text-red-500' : 'bg-white border-gray-200 text-blue-500'}`}>
                                                {contato.prioritario ? <ShieldAlert className="w-5 h-5" /> : <Users className="w-5 h-5" />}
                                            </div>
                                            <div>
                                                <div className="flex items-center gap-2">
                                                    <h5 className="font-bold text-gray-900">{contato.nome}</h5>
                                                    <span className="text-xs px-2 py-0.5 bg-gray-200 rounded text-gray-600 font-bold uppercase">{contato.parentesco}</span>
                                                    {contato.prioritario && <span className="text-[10px] px-2 py-0.5 bg-red-100 text-red-600 rounded-full font-black uppercase">Emergência</span>}
                                                </div>
                                                <p className="text-sm text-gray-500 mt-1 flex items-center gap-1">
                                                    <Phone className="w-3 h-3" /> {contato.telefone}
                                                </p>
                                                <div className="flex gap-2 mt-3">
                                                    {contato.canais.map(c => (
                                                        <span key={c} className="px-2 py-1 bg-white border border-gray-200 rounded-lg text-[10px] font-bold text-gray-500 flex items-center gap-1">
                                                            <MessageSquare className="w-3 h-3 text-blue-400" /> {c}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => handleRemove(contato.id)}
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
                                    <label className="block text-sm font-bold text-gray-700 mb-1">Nome Completo</label>
                                    <input
                                        type="text" required
                                        className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
                                        placeholder="Ex: João Silva"
                                        value={novoContato.nome}
                                        onChange={e => setNovoContato({ ...novoContato, nome: e.target.value })}
                                    />
                                </div>
                                <div className="col-span-2 sm:col-span-1">
                                    <label className="block text-sm font-bold text-gray-700 mb-1">Parentesco/Vínculo</label>
                                    <input
                                        type="text" required
                                        className="w-full p-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
                                        placeholder="Ex: Filho, Médico, Vizinho"
                                        value={novoContato.parentesco}
                                        onChange={e => setNovoContato({ ...novoContato, parentesco: e.target.value })}
                                    />
                                </div>
                                <div className="col-span-2">
                                    <label className="block text-sm font-bold text-gray-700 mb-1">Telefone (com DDD)</label>
                                    <input
                                        type="tel" required
                                        className="w-full p-2 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 outline-none"
                                        placeholder="Ex: (11) 99999-9999"
                                        value={novoContato.telefone}
                                        onChange={e => setNovoContato({ ...novoContato, telefone: e.target.value })}
                                    />
                                </div>

                                <div className="col-span-2">
                                    <label className="block text-sm font-bold text-gray-700 mb-3">Canais de Notificação</label>
                                    <div className="flex gap-4">
                                        {['SMS', 'WhatsApp', 'Email'].map(canal => (
                                            <button
                                                key={canal}
                                                type="button"
                                                onClick={() => toggleCanal(canal)}
                                                className={`flex-1 py-3 border-2 rounded-2xl font-bold transition-all ${novoContato.canais.includes(canal) ? 'border-blue-600 bg-blue-50 text-blue-600' : 'border-gray-100 bg-gray-50 text-gray-400'}`}
                                            >
                                                {canal}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="col-span-2 flex items-center gap-3 p-4 bg-red-50 rounded-2xl border border-red-100">
                                    <input
                                        type="checkbox"
                                        id="prioritario"
                                        className="w-5 h-5 accent-red-500"
                                        checked={novoContato.prioritario}
                                        onChange={e => setNovoContato({ ...novoContato, prioritario: e.target.checked })}
                                    />
                                    <label htmlFor="prioritario" className="text-sm font-bold text-red-700 cursor-pointer">
                                        Definir como Contato de Emergência Crítica
                                    </label>
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
                                    className="flex-1 py-3 px-6 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 shadow-lg shadow-blue-200 transition-colors"
                                >
                                    Salvar Contato
                                </button>
                            </div>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
}
