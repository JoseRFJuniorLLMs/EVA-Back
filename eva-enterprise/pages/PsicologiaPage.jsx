import React from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area,
    BarChart, Bar, Legend
} from 'recharts';
import { Brain, Heart, TrendingUp, MessageCircle, AlertCircle, Quote, Sparkles, Filter } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';

export default function PsicologiaPage() {
    const { emotionalAnalytics, idosos, loading } = useEva();

    if (loading || !emotionalAnalytics) {
        return <div className="p-8 text-center text-indigo-600 font-bold">Analisando ondas cerebrais e sentimentos...</div>;
    }

    const InsightCard = ({ insight }) => (
        <div className={`p-5 rounded-3xl border ${insight.tipo === 'positivo' ? 'bg-emerald-50 border-emerald-100' :
                insight.tipo === 'alerta' ? 'bg-red-50 border-red-100' : 'bg-indigo-50 border-indigo-100'
            } flex gap-4 animate-in slide-in-from-right duration-500`}>
            <div className={`p-3 rounded-2xl shrink-0 ${insight.tipo === 'positivo' ? 'bg-emerald-100 text-emerald-600' :
                    insight.tipo === 'alerta' ? 'bg-red-100 text-red-600' : 'bg-indigo-100 text-indigo-600'
                }`}>
                {insight.tipo === 'positivo' ? <Heart className="w-5 h-5" /> :
                    insight.tipo === 'alerta' ? <AlertCircle className="w-5 h-5" /> : <Sparkles className="w-5 h-5" />}
            </div>
            <div>
                <p className="text-gray-800 font-medium leading-relaxed text-sm">{insight.mensagem}</p>
                <div className="flex items-center gap-2 mt-2">
                    <span className="text-[10px] font-black uppercase tracking-widest opacity-40">{insight.data}</span>
                    <span className="text-gray-300">•</span>
                    <span className="text-[10px] font-bold text-indigo-400 uppercase">Insight IA</span>
                </div>
            </div>
        </div>
    );

    return (
        <div className="p-8 space-y-8 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <div className="p-4 bg-indigo-600 text-white rounded-[2rem] shadow-xl shadow-indigo-100">
                        <Brain className="w-8 h-8" />
                    </div>
                    <div>
                        <h2 className="text-3xl font-black text-gray-900 tracking-tight">Psicologia Digital</h2>
                        <p className="text-gray-500 font-medium">Análise de sentimentos e acolhimento humano via IA</p>
                    </div>
                </div>
                <div className="flex gap-3">
                    <button className="flex items-center gap-2 px-5 py-2.5 bg-white border border-gray-200 rounded-2xl text-sm font-bold text-gray-600 hover:bg-gray-50 transition-all">
                        <Filter className="w-4 h-4" /> Todos os Idosos
                    </button>
                    <button className="px-5 py-2.5 bg-indigo-600 text-white rounded-2xl text-sm font-black hover:bg-indigo-700 shadow-lg shadow-indigo-100 transition-all active:scale-95">
                        Gerar Plano de Acolhimento
                    </button>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Evolution Chart */}
                <div className="lg:col-span-2 bg-white p-8 rounded-[2.5rem] shadow-xl border border-gray-50">
                    <div className="flex justify-between items-center mb-8">
                        <div>
                            <h3 className="text-xl font-black text-gray-900 leading-tight">Mapa de Calor Emocional</h3>
                            <p className="text-sm text-gray-500 font-medium mt-1">Tendência predominante nos últimos 7 dias</p>
                        </div>
                        <div className="flex items-center gap-4 text-xs font-black uppercase tracking-widest">
                            <span className="flex items-center gap-1.5 text-emerald-500"><div className="w-2 h-2 rounded-full bg-emerald-500" /> Feliz</span>
                            <span className="flex items-center gap-1.5 text-amber-500"><div className="w-2 h-2 rounded-full bg-amber-500" /> Neutro</span>
                            <span className="flex items-center gap-1.5 text-red-500"><div className="w-2 h-2 rounded-full bg-red-500" /> Triste</span>
                        </div>
                    </div>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={emotionalAnalytics.historico}>
                                <defs>
                                    <linearGradient id="colorFeliz" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.1} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis
                                    dataKey="data"
                                    axisLine={false}
                                    tickLine={false}
                                    tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 700 }}
                                    dy={10}
                                />
                                <YAxis hide />
                                <Tooltip
                                    contentStyle={{ borderRadius: '24px', border: 'none', boxShadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)' }}
                                />
                                <Area type="monotone" dataKey="feliz" stroke="#10b981" strokeWidth={4} fillOpacity={1} fill="url(#colorFeliz)" stackId="1" />
                                <Area type="monotone" dataKey="neutro" stroke="#f59e0b" strokeWidth={4} fillOpacity={0} stackId="1" />
                                <Area type="monotone" dataKey="triste" stroke="#ef4444" strokeWidth={4} fillOpacity={0} stackId="1" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Topics Cloud */}
                <div className="bg-white p-8 rounded-[2.5rem] shadow-xl border border-gray-50 flex flex-col">
                    <h3 className="text-xl font-black text-gray-900 leading-tight mb-2">Nuvem Afetiva</h3>
                    <p className="text-sm text-gray-500 font-medium mb-8">Tópicos mais citados em tons positivos</p>

                    <div className="flex flex-wrap gap-3 flex-1 items-center justify-center content-center">
                        {emotionalAnalytics.nuvemTopicos.map((topic, i) => (
                            <span
                                key={topic.texto}
                                className={`px-4 py-2 rounded-2xl font-black uppercase tracking-widest transition-all hover:scale-110 cursor-default ${i === 0 ? 'bg-indigo-600 text-white text-lg' :
                                        i === 1 ? 'bg-pink-100 text-pink-600 text-sm' :
                                            i === 2 ? 'bg-emerald-100 text-emerald-600 text-md' :
                                                'bg-gray-100 text-gray-400 text-xs'
                                    }`}
                                style={{ opacity: topic.valor / 100 }}
                            >
                                {topic.texto}
                            </span>
                        ))}
                    </div>
                </div>

                {/* Insights Section */}
                <div className="bg-white p-8 rounded-[2.5rem] shadow-xl border border-gray-50 lg:col-span-1">
                    <div className="flex items-center gap-3 mb-6">
                        <TrendingUp className="w-5 h-5 text-indigo-600" />
                        <h3 className="text-xl font-black text-gray-900 leading-tight">Observações Clínicas</h3>
                    </div>
                    <div className="space-y-4">
                        {emotionalAnalytics.insights.map(insight => (
                            <InsightCard key={insight.id} insight={insight} />
                        ))}
                    </div>
                </div>

                {/* Actionable Plan */}
                <div className="bg-gradient-to-br from-indigo-600 to-indigo-800 p-8 rounded-[2.5rem] shadow-xl lg:col-span-2 text-white relative overflow-hidden group">
                    <div className="absolute top-0 right-0 p-12 opacity-10 group-hover:scale-110 transition-transform">
                        <Sparkles className="w-32 h-32" />
                    </div>
                    <div className="relative z-10">
                        <h3 className="text-2xl font-black mb-4">Plano de Intervenção Sugerido</h3>
                        <p className="text-indigo-100 font-medium leading-relaxed mb-8 max-w-xl">
                            Com base nos padrões detectados, a EVA recomenda uma abordagem de **"Validação de Memória"**.
                            O idoso está em um ciclo de reminiscência positiva sobre a juventude.
                        </p>
                        <ul className="space-y-4 mb-8">
                            <li className="flex items-start gap-3">
                                <div className="p-1 bg-white/20 rounded-lg mt-1"><Sparkles className="w-3 h-3" /></div>
                                <span className="text-sm font-bold">Injetar perguntas sobre "Profissão" no próximo prompt.</span>
                            </li>
                            <li className="flex items-start gap-3">
                                <div className="p-1 bg-white/20 rounded-lg mt-1"><Sparkles className="w-3 h-3" /></div>
                                <span className="text-sm font-bold">Disparar um áudio de incentivo do neto (Joãozinho) às 15h.</span>
                            </li>
                        </ul>
                        <button className="px-8 py-3 bg-white text-indigo-600 rounded-2xl font-black shadow-xl hover:bg-indigo-50 transition-all active:scale-95">
                            Ativar Estratégia Agora
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
