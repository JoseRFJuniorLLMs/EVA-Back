import React, { useState } from 'react';
import { X, Sparkles, Plus, Play, Music, Image as ImageIcon, Trash2, Send, Clock, User } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';

export default function LegadoDigitalModal({ isOpen, onClose, idoso }) {
    const { legacyAssets, setLegacyAssets } = useEva();
    const [filter, setFilter] = useState('todos');

    if (!isOpen || !idoso) return null;

    const assets = legacyAssets.filter(a => a.idoso_id === idoso.id);
    const filteredAssets = filter === 'todos' ? assets : assets.filter(a => a.tipo === filter);

    const getIcon = (tipo) => {
        switch (tipo) {
            case 'audio': return <Music className="w-5 h-5 text-purple-500" />;
            case 'video': return <Play className="w-5 h-5 text-blue-500" />;
            case 'imagem': return <ImageIcon className="w-5 h-5 text-emerald-500" />;
            default: return <Sparkles className="w-5 h-5 text-pink-500" />;
        }
    };

    const handleDelete = (id) => {
        setLegacyAssets(legacyAssets.filter(a => a.id !== id));
    };

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[150] flex items-center justify-center p-4">
            <div className="bg-white w-full max-w-2xl rounded-[2.5rem] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
                {/* Header Compacto */}
                <div className="p-5 border-b border-gray-100 flex justify-between items-center bg-gradient-to-r from-indigo-50 to-white">
                    <div className="flex items-center gap-4">
                        <div className="p-2 bg-indigo-100 rounded-2xl text-indigo-600">
                            <Sparkles className="w-6 h-6" />
                        </div>
                        <div>
                            <h3 className="text-xl font-black text-gray-900 leading-tight">Legado Digital</h3>
                            <p className="text-sm text-gray-500 font-medium tracking-tight">Cápsula do Tempo de {idoso.nome}</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                        <X className="w-6 h-6 text-gray-400" />
                    </button>
                </div>

                <div className="p-6">
                    {/* Filtros e Ação */}
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex bg-gray-100 p-1 rounded-xl">
                            {['todos', 'audio', 'video', 'imagem'].map((t) => (
                                <button
                                    key={t}
                                    onClick={() => setFilter(t)}
                                    className={`px-4 py-1.5 rounded-lg text-xs font-bold uppercase tracking-widest transition-all ${filter === t ? 'bg-white text-indigo-600 shadow-sm' : 'text-gray-400 hover:text-gray-600'}`}
                                >
                                    {t}
                                </button>
                            ))}
                        </div>
                        <button className="flex items-center gap-2 px-4 py-2 bg-indigo-600 text-white rounded-xl font-bold text-sm hover:bg-indigo-700 shadow-lg shadow-indigo-100 transition-all active:scale-95">
                            <Plus className="w-4 h-4" /> Adicionar Lembrança
                        </button>
                    </div>

                    {/* Lista de Assets */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                        {filteredAssets.length === 0 ? (
                            <div className="col-span-2 text-center py-12 bg-gray-50 rounded-3xl border-2 border-dashed border-gray-100">
                                <Sparkles className="w-12 h-12 text-gray-200 mx-auto mb-3" />
                                <p className="text-gray-400 font-medium italic">Nenhuma lembrança nesta categoria.</p>
                            </div>
                        ) : (
                            filteredAssets.map(asset => (
                                <div key={asset.id} className="group p-4 bg-white border border-gray-100 rounded-3xl hover:border-indigo-200 hover:shadow-lg hover:shadow-indigo-50 transition-all flex flex-col gap-3 relative">
                                    <div className="flex items-center gap-3">
                                        <div className="p-2 bg-gray-50 rounded-xl group-hover:bg-indigo-50 transition-colors">
                                            {getIcon(asset.tipo)}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <h4 className="font-bold text-gray-900 truncate leading-tight">{asset.titulo}</h4>
                                            <div className="flex items-center gap-2 mt-1">
                                                <span className="text-[10px] font-black uppercase text-gray-400 tracking-widest">{asset.tipo}</span>
                                                <span className="text-[10px] text-gray-300">•</span>
                                                <span className="text-[10px] font-medium text-gray-400">{asset.data}</span>
                                            </div>
                                        </div>
                                        <button
                                            onClick={() => handleDelete(asset.id)}
                                            className="opacity-0 group-hover:opacity-100 p-2 text-gray-300 hover:text-red-500 transition-all"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>

                                    {asset.tipo === 'imagem' && (
                                        <div className="h-24 w-full rounded-2xl overflow-hidden border border-gray-50">
                                            <img src={asset.url} alt={asset.titulo} className="w-full h-full object-cover grayscale-[20%] group-hover:grayscale-0 transition-all" />
                                        </div>
                                    )}

                                    <div className="flex items-center justify-between pt-2 border-t border-gray-50">
                                        <div className="flex items-center gap-1.5 text-indigo-600 bg-indigo-50 px-2 py-1 rounded-lg">
                                            <User className="w-3 h-3" />
                                            <span className="text-[10px] font-black uppercase tracking-tight">Para: {asset.destinatario}</span>
                                        </div>
                                        <button className="text-gray-400 hover:text-indigo-600 transition-colors">
                                            <Clock className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                <div className="p-5 bg-indigo-600 text-white">
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-white/20 rounded-xl">
                                <Send className="w-5 h-5" />
                            </div>
                            <div>
                                <p className="text-xs font-bold leading-tight uppercase tracking-widest">Ativação Pós-Transição</p>
                                <p className="text-[10px] opacity-80 mt-0.5">Automático via Equipe de Cuidado</p>
                            </div>
                        </div>
                        <div className="flex gap-2">
                            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse shadow-[0_0_8px_rgba(74,222,128,0.5)]"></div>
                            <span className="text-[10px] font-black uppercase tracking-[0.1em]">Protegido</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
