import React, { useState } from 'react';
import {
    Activity, Heart, Thermometer, Droplets,
    X, Plus, LineChart, Calendar, AlertCircle, Save
} from 'lucide-react';
import { useEva } from '../contexts/EvaContext';

export default function SinaisVitaisModal({ isOpen, onClose, idoso }) {
    const { sinaisVitais, setSinaisVitais } = useEva();
    const [isAdding, setIsAdding] = useState(false);
    const [newData, setNewData] = useState({ tipo: 'Pressão Arterial', valor: '', unidade: 'mmHg' });

    if (!isOpen || !idoso) return null;

    const metrics = sinaisVitais.filter(s => s.idoso_id === idoso.id);

    const handleSave = () => {
        const item = {
            id: Date.now(),
            idoso_id: idoso.id,
            ...newData,
            data: new Date().toLocaleString(),
            status: 'normal'
        };
        setSinaisVitais([item, ...sinaisVitais]);
        setIsAdding(false);
        setNewData({ tipo: 'Pressão Arterial', valor: '', unidade: 'mmHg' });
    };

    const getIcon = (tipo) => {
        switch (tipo) {
            case 'Pressão Arterial': return <Heart className="w-5 h-5" />;
            case 'Glicose': return <Droplets className="w-5 h-5" />;
            case 'Temperatura': return <Thermometer className="w-5 h-5" />;
            default: return <Activity className="w-5 h-5" />;
        }
    };

    const getColor = (tipo) => {
        switch (tipo) {
            case 'Pressão Arterial': return 'text-red-500 bg-red-50';
            case 'Glicose': return 'text-blue-500 bg-blue-50';
            case 'Temperatura': return 'text-amber-500 bg-amber-50';
            default: return 'text-indigo-500 bg-indigo-50';
        }
    };

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[200] flex items-center justify-center p-4">
            <div className="bg-white w-full max-w-2xl rounded-[2.5rem] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
                {/* Header */}
                <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gradient-to-r from-emerald-50 to-white">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-emerald-600 text-white rounded-2xl shadow-lg shadow-emerald-100">
                            <Activity className="w-6 h-6" />
                        </div>
                        <div>
                            <h3 className="text-xl font-black text-gray-900">Sinais Vitais</h3>
                            <p className="text-sm text-gray-500 font-medium">{idoso.nome}</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                        <X className="w-6 h-6 text-gray-400" />
                    </button>
                </div>

                <div className="p-8">
                    {isAdding ? (
                        <div className="space-y-6 animate-in slide-in-from-bottom duration-300">
                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <label className="text-xs font-black text-gray-400 uppercase tracking-widest px-1">Tipo de Medição</label>
                                    <select
                                        value={newData.tipo}
                                        onChange={(e) => setNewData({ ...newData, tipo: e.target.value, unidade: e.target.value === 'Glicose' ? 'mg/dL' : e.target.value === 'Temperatura' ? '°C' : 'mmHg' })}
                                        className="w-full p-4 bg-gray-50 border-2 border-transparent focus:border-emerald-500 rounded-2xl outline-none font-bold transition-all"
                                    >
                                        <option>Pressão Arterial</option>
                                        <option>Glicose</option>
                                        <option>Temperatura</option>
                                    </select>
                                </div>
                                <div className="space-y-2">
                                    <label className="text-xs font-black text-gray-400 uppercase tracking-widest px-1">Valor</label>
                                    <div className="relative">
                                        <input
                                            type="text"
                                            placeholder="Ex: 12/8"
                                            value={newData.valor}
                                            onChange={(e) => setNewData({ ...newData, valor: e.target.value })}
                                            className="w-full p-4 bg-gray-50 border-2 border-transparent focus:border-emerald-500 rounded-2xl outline-none font-bold transition-all pr-16"
                                        />
                                        <span className="absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 font-bold text-sm">{newData.unidade}</span>
                                    </div>
                                </div>
                            </div>
                            <div className="flex gap-3 pt-4">
                                <button onClick={() => setIsAdding(false)} className="flex-1 py-4 bg-gray-100 text-gray-600 rounded-2xl font-black hover:bg-gray-200 transition-all">Cancelar</button>
                                <button onClick={handleSave} className="flex-1 py-4 bg-emerald-600 text-white rounded-2xl font-black shadow-lg shadow-emerald-100 hover:bg-emerald-700 transition-all flex items-center justify-center gap-2">
                                    <Save className="w-5 h-5" /> Salvar Medição
                                </button>
                            </div>
                        </div>
                    ) : (
                        <div className="space-y-6">
                            <div className="flex justify-between items-center">
                                <h4 className="text-sm font-black text-gray-400 uppercase tracking-widest">Histórico Recente</h4>
                                <button
                                    onClick={() => setIsAdding(true)}
                                    className="flex items-center gap-2 px-4 py-2 bg-emerald-50 text-emerald-600 rounded-xl font-bold text-sm hover:bg-emerald-100 transition-all"
                                >
                                    <Plus className="w-4 h-4" /> Nova Medição
                                </button>
                            </div>

                            <div className="grid grid-cols-1 gap-3 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
                                {metrics.length > 0 ? metrics.map((metric) => (
                                    <div key={metric.id} className="p-4 bg-white border border-gray-100 rounded-2xl flex items-center justify-between group hover:border-emerald-200 transition-all shadow-sm">
                                        <div className="flex items-center gap-4">
                                            <div className={`p-3 rounded-xl ${getColor(metric.tipo)}`}>
                                                {getIcon(metric.tipo)}
                                            </div>
                                            <div>
                                                <p className="font-black text-gray-900 leading-tight">{metric.tipo}</p>
                                                <div className="flex items-center gap-2 mt-1">
                                                    <Calendar className="w-3 h-3 text-gray-400" />
                                                    <span className="text-[10px] font-bold text-gray-400">{metric.data}</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div className="text-right">
                                            <p className="text-xl font-black text-emerald-600">{metric.valor} <span className="text-[10px] text-gray-400">{metric.unidade}</span></p>
                                            {metric.status === 'alerta' && (
                                                <span className="text-[8px] font-black uppercase text-red-500 px-2 py-0.5 bg-red-50 rounded-full border border-red-100 inline-block mt-1 animate-pulse">
                                                    Alerta
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                )) : (
                                    <div className="text-center py-12 bg-gray-50 rounded-3xl border-2 border-dashed border-gray-100 text-gray-400 font-medium">
                                        Nenhuma medição registrada recentemente.
                                    </div>
                                )}
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer Insight */}
                {!isAdding && (
                    <div className="p-6 bg-emerald-900 text-white rounded-b-[2.5rem] flex items-start gap-4 mx-2 mb-2">
                        <div className="p-2 bg-white/10 rounded-xl">
                            <LineChart className="w-5 h-5" />
                        </div>
                        <div>
                            <p className="text-xs font-black uppercase tracking-widest opacity-60 mb-1">Análise da EVA</p>
                            <p className="text-sm font-medium leading-relaxed">
                                Os níveis de glicose e pressão estão estáveis nos últimos 7 dias. Recomendo manter a dieta atual.
                            </p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
