import React, { useState } from 'react';
import { X, Search, Plus, Trash2, Heart, Award, Music, Briefcase, Users } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';

export default function MemoriaAfetivaModal({ isOpen, onClose, idoso }) {
    const { biografiaIdosos, setBiografiaIdosos } = useEva();
    const [searchTerm, setSearchTerm] = useState('');
    const [showAddForm, setShowAddForm] = useState(false);
    const [newFact, setNewFact] = useState({ categoria: 'Família', fato: '', relevancia: 'media' });

    if (!isOpen || !idoso) return null;

    const fatosIdoso = biografiaIdosos.filter(b => b.idoso_id === idoso.id);
    const filteredFatos = fatosIdoso.filter(f =>
        f.fato.toLowerCase().includes(searchTerm.toLowerCase()) ||
        f.categoria.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleAddFact = (e) => {
        e.preventDefault();
        const id = Math.max(0, ...biografiaIdosos.map(f => f.id)) + 1;
        setBiografiaIdosos([...biografiaIdosos, { ...newFact, id, idoso_id: idoso.id }]);
        setNewFact({ categoria: 'Família', fato: '', relevancia: 'media' });
        setShowAddForm(false);
    };

    const handleDelete = (id) => {
        setBiografiaIdosos(biografiaIdosos.filter(f => f.id !== id));
    };

    const getIcon = (cat) => {
        switch (cat) {
            case 'Família': return <Users className="w-5 h-5 text-blue-500" />;
            case 'Hobbies': return <Music className="w-5 h-5 text-purple-500" />;
            case 'Profissão': return <Briefcase className="w-5 h-5 text-amber-500" />;
            case 'Conquistas': return <Award className="w-5 h-5 text-yellow-500" />;
            default: return <Heart className="w-5 h-5 text-pink-500" />;
        }
    }

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[150] flex items-center justify-center p-4">
            <div className="bg-white w-full max-w-2xl rounded-[2.5rem] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
                <div className="p-8 border-b border-gray-100 flex justify-between items-center bg-gradient-to-r from-pink-50 to-white">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-pink-100 rounded-2xl text-pink-600">
                            <Heart className="w-8 h-8" />
                        </div>
                        <div>
                            <h3 className="text-2xl font-black text-gray-900 leading-tight">Memória Afetiva</h3>
                            <p className="text-gray-500 font-medium">Conhecimento pessoal de {idoso.nome}</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                        <X className="w-8 h-8 text-gray-400" />
                    </button>
                </div>

                <div className="p-8">
                    <div className="flex gap-4 mb-6">
                        <div className="flex-1 relative">
                            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Buscar fatos, nomes, hobbies..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-100 rounded-2xl focus:outline-none focus:border-pink-400 transition-colors font-medium shadow-inner"
                            />
                        </div>
                        <button
                            onClick={() => setShowAddForm(!showAddForm)}
                            className="bg-pink-600 text-white p-3 rounded-2xl hover:bg-pink-700 shadow-lg shadow-pink-200 transition-all"
                        >
                            <Plus className="w-6 h-6" />
                        </button>
                    </div>

                    {showAddForm && (
                        <form onSubmit={handleAddFact} className="mb-8 p-6 bg-pink-50/50 rounded-3xl border-2 border-dashed border-pink-200 animate-in slide-in-from-top-4 duration-300">
                            <div className="grid grid-cols-2 gap-4 mb-4">
                                <div>
                                    <label className="block text-xs font-black text-pink-700 uppercase tracking-widest mb-2">Categoria</label>
                                    <select
                                        value={newFact.categoria}
                                        onChange={(e) => setNewFact({ ...newFact, categoria: e.target.value })}
                                        className="w-full p-3 bg-white border border-pink-100 rounded-xl focus:outline-none focus:border-pink-400 font-bold text-gray-700"
                                    >
                                        <option>Família</option>
                                        <option>Hobbies</option>
                                        <option>Profissão</option>
                                        <option>Conquistas</option>
                                        <option>Outros</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-xs font-black text-pink-700 uppercase tracking-widest mb-2">Relevância</label>
                                    <select
                                        value={newFact.relevancia}
                                        onChange={(e) => setNewFact({ ...newFact, relevancia: e.target.value })}
                                        className="w-full p-3 bg-white border border-pink-100 rounded-xl focus:outline-none focus:border-pink-400 font-bold text-gray-700"
                                    >
                                        <option value="alta">Alta (Prioritário no prompt)</option>
                                        <option value="media">Média</option>
                                        <option value="baixa">Baixa</option>
                                    </select>
                                </div>
                            </div>
                            <div className="mb-4">
                                <label className="block text-xs font-black text-pink-700 uppercase tracking-widest mb-2">Fato Biográfico</label>
                                <textarea
                                    required
                                    placeholder="Ex: Adora ser chamada de Dona Mariquinha e tem 4 netos (Bia, Léo, Clarinha e Gabi)."
                                    value={newFact.fato}
                                    onChange={(e) => setNewFact({ ...newFact, fato: e.target.value })}
                                    className="w-full p-4 bg-white border border-pink-100 rounded-xl focus:outline-none focus:border-pink-400 font-medium text-gray-700 h-24 resize-none shadow-inner"
                                />
                            </div>
                            <div className="flex justify-end gap-3">
                                <button type="button" onClick={() => setShowAddForm(false)} className="px-6 py-2 text-gray-500 font-bold hover:text-pink-600 transition-colors">Cancelar</button>
                                <button type="submit" className="px-8 py-2 bg-pink-600 text-white rounded-xl font-black shadow-lg shadow-pink-100 hover:bg-pink-700 transition-colors">Salvar Fato</button>
                            </div>
                        </form>
                    )}

                    <div className="max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                        {filteredFatos.length === 0 ? (
                            <div className="text-center py-12 text-gray-400">
                                <p className="font-medium italic">Nenhum fato registrado ainda.</p>
                                <p className="text-xs mt-1">Dê personalidade à EVA adicionando histórias!</p>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {filteredFatos.map(fato => (
                                    <div key={fato.id} className="group p-5 bg-white border border-gray-100 rounded-3xl hover:border-pink-200 hover:shadow-lg hover:shadow-pink-50 transition-all flex items-start gap-4 relative">
                                        <div className="p-3 bg-gray-50 rounded-2xl group-hover:bg-pink-50 transition-colors">
                                            {getIcon(fato.categoria)}
                                        </div>
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className="text-[10px] font-black uppercase text-gray-400 tracking-widest">{fato.categoria}</span>
                                                <span className={`px-2 py-0.5 rounded-md text-[8px] font-black uppercase tracking-widest ${fato.relevancia === 'alta' ? 'bg-red-100 text-red-600' :
                                                        fato.relevancia === 'media' ? 'bg-blue-100 text-blue-600' : 'bg-gray-100 text-gray-400'
                                                    }`}>
                                                    Relevância {fato.relevancia}
                                                </span>
                                            </div>
                                            <p className="text-gray-700 font-medium leading-relaxed">{fato.fato}</p>
                                        </div>
                                        <button
                                            onClick={() => handleDelete(fato.id)}
                                            className="opacity-0 group-hover:opacity-100 p-2 text-gray-400 hover:text-red-500 transition-all"
                                        >
                                            <Trash2 className="w-5 h-5" />
                                        </button>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                <div className="p-8 bg-gray-50 text-center">
                    <p className="text-[10px] text-gray-400 font-black uppercase tracking-[0.2em] leading-relaxed">
                        Estes dados injetam contexto afetivo nos prompts da EVA em tempo real.
                    </p>
                </div>
            </div>
        </div>
    );
}
