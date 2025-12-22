import React from 'react';
import { X, History, Phone, Pill, AlertTriangle, Users, Heart, Clock } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';

export default function TimelineModal({ isOpen, onClose, idoso }) {
    const { timelineData } = useEva();

    if (!isOpen || !idoso) return null;

    const items = timelineData.filter(item => item.idoso_id === idoso.id);

    const getIcon = (tipo, subtipo) => {
        switch (tipo) {
            case 'ligacao':
                return subtipo === 'emocional' ? <Heart className="w-5 h-5" /> : <Phone className="w-5 h-5" />;
            case 'medicamento': return <Pill className="w-5 h-5" />;
            case 'alerta': return <AlertTriangle className="w-5 h-5" />;
            case 'equipe': return <Users className="w-5 h-5" />;
            default: return <History className="w-5 h-5" />;
        }
    };

    const getColor = (tipo, subtipo) => {
        if (subtipo === 'critico') return 'bg-red-500 text-white shadow-red-100';
        switch (tipo) {
            case 'ligacao': return 'bg-pink-500 text-white shadow-pink-100';
            case 'medicamento': return 'bg-purple-500 text-white shadow-purple-100';
            case 'alerta': return 'bg-amber-500 text-white shadow-amber-100';
            case 'equipe': return 'bg-blue-500 text-white shadow-blue-100';
            default: return 'bg-gray-500 text-white shadow-gray-100';
        }
    };

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[110] flex items-center justify-center p-4 animate-in fade-in duration-300">
            <div className="bg-pink-50 w-full max-w-2xl rounded-[2.5rem] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-500 h-[85vh] flex flex-col">

                {/* Header */}
                <div className="p-5 bg-white border-b flex justify-between items-center shrink-0">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-pink-100 rounded-2xl flex items-center justify-center text-pink-600">
                            <History className="w-6 h-6" />
                        </div>
                        <div>
                            <h2 className="text-xl font-black text-gray-900 leading-tight">Timeline 360º</h2>
                            <p className="text-sm text-gray-500 font-medium">Histórico unificado de {idoso.nome}</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 text-gray-300 hover:text-gray-600 transition-colors">
                        <X className="w-6 h-6" />
                    </button>
                </div>

                {/* Timeline Body */}
                <div className="flex-1 overflow-y-auto p-6 relative">
                    {/* The Vertical Line */}
                    <div className="absolute left-14 top-8 bottom-8 w-1 bg-gradient-to-b from-pink-100 via-purple-100 to-pink-50 rounded-full" />

                    <div className="space-y-6 relative">
                        {items.length === 0 ? (
                            <div className="text-center py-20">
                                <p className="text-gray-400 font-bold">Nenhuma atividade registrada ainda.</p>
                            </div>
                        ) : (
                            items.map((item) => (
                                <div key={item.id} className="flex gap-8 group">
                                    {/* Icon / Bullet */}
                                    <div className={`shrink-0 w-10 h-10 rounded-2xl flex items-center justify-center shadow-lg transition-transform group-hover:scale-110 z-10 ${getColor(item.tipo, item.subtipo)}`}>
                                        {getIcon(item.tipo, item.subtipo)}
                                    </div>

                                    {/* Content Card */}
                                    <div className="flex-1 bg-white p-4 rounded-3xl shadow-md border border-gray-100 hover:shadow-xl transition-all hover:-translate-y-1">
                                        <div className="flex justify-between items-start mb-2">
                                            <h3 className="font-black text-gray-900 uppercase text-xs tracking-widest">{item.titulo}</h3>
                                            <div className="flex items-center gap-1 text-[10px] font-bold text-gray-400 bg-gray-50 px-2 py-1 rounded-lg">
                                                <Clock className="w-3 h-3" />
                                                {item.data}
                                            </div>
                                        </div>
                                        <p className="text-gray-600 text-sm leading-relaxed mt-2 font-medium">
                                            {item.descricao}
                                        </p>

                                        {/* Dynamic Badges based on type */}
                                        <div className="mt-4 flex gap-2">
                                            <span className={`text-[10px] font-black px-2 py-1 rounded-md uppercase tracking-tighter ${item.subtipo === 'critico' ? 'bg-red-100 text-red-600' :
                                                item.subtipo === 'sucesso' ? 'bg-green-100 text-green-600' :
                                                    'bg-gray-100 text-gray-500'
                                                }`}>
                                                {item.tipo}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Footer Insight */}
                <div className="p-4 bg-pink-600 text-white shrink-0 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-white/20 rounded-xl">
                            <Heart className="w-5 h-5" />
                        </div>
                        <p className="text-sm font-bold">Insight da EVA: "Dona Maria está mantendo uma rotina estável."</p>
                    </div>
                    <button className="text-xs font-black uppercase tracking-widest bg-white/10 px-4 py-2 rounded-xl border border-white/20 hover:bg-white/20 transition-all">
                        Ver Mais
                    </button>
                </div>
            </div>
        </div>
    );
}
