import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, AreaChart, Area } from 'recharts';
import { Wallet, TrendingUp, Cpu, Phone, Download, Filter, Info } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';

export default function FinOpsPage() {
    const { dadosFinOps } = useEva();

    if (!dadosFinOps) return <div className="p-8 text-pink-600 font-bold">Carregando dados financeiros...</div>;

    return (
        <div className="p-8 space-y-10">
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-3xl font-black text-gray-900 leading-tight flex items-center gap-3">
                        <Wallet className="w-8 h-8 text-pink-600" />
                        FinOps Dashboard
                    </h2>
                    <p className="text-gray-500 font-medium mt-1">Gestão de Custos e Margem de Operação</p>
                </div>
                <button className="flex items-center gap-2 px-6 py-3 bg-pink-600 text-white rounded-2xl hover:bg-pink-700 shadow-lg shadow-pink-100 font-black transition-all">
                    <Download className="w-5 h-5" />
                    Exportar Relatório
                </button>
            </div>

            {/* KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white p-8 rounded-[2rem] shadow-xl border border-pink-50">
                    <span className="text-[10px] font-black uppercase text-gray-400 tracking-[0.2em] mb-2 block">Custo Total (Mês)</span>
                    <div className="text-3xl font-black text-pink-600">R$ {dadosFinOps.totalMensal.toLocaleString('pt-BR')}</div>
                    <div className="mt-2 flex items-center gap-1 text-green-500 font-bold text-xs">
                        <TrendingUp className="w-4 h-4" /> +12% vs mês anterior
                    </div>
                </div>
                <div className="bg-white p-8 rounded-[2rem] shadow-xl border border-pink-50">
                    <span className="text-[10px] font-black uppercase text-gray-400 tracking-[0.2em] mb-2 block">Média por Idoso</span>
                    <div className="text-3xl font-black text-gray-900">R$ {(dadosFinOps.totalMensal / dadosFinOps.porIdoso.length).toLocaleString('pt-BR')}</div>
                    <div className="mt-2 text-gray-400 font-medium text-xs">Base: {dadosFinOps.porIdoso.length} idosos ativos</div>
                </div>
                <div className="bg-white p-8 rounded-[2rem] shadow-xl border border-pink-50">
                    <span className="text-[10px] font-black uppercase text-gray-400 tracking-[0.2em] mb-2 block">Tokens Gemini</span>
                    <div className="text-3xl font-black text-indigo-600">183k</div>
                    <div className="mt-2 flex items-center gap-1 text-indigo-400 font-bold text-xs">
                        <Cpu className="w-4 h-4" /> 2.1 tokens/minuto média
                    </div>
                </div>
                <div className="bg-white p-8 rounded-[2rem] shadow-xl border border-pink-50">
                    <span className="text-[10px] font-black uppercase text-gray-400 tracking-[0.2em] mb-2 block">Minutos Twilio</span>
                    <div className="text-3xl font-black text-emerald-600">1.250</div>
                    <div className="mt-2 flex items-center gap-1 text-emerald-400 font-bold text-xs">
                        <Phone className="w-4 h-4" /> 0.85% de falhas
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Gráfico de Evolução */}
                <div className="bg-white p-10 rounded-[2.5rem] shadow-xl border border-pink-50">
                    <h3 className="text-xl font-black text-gray-900 mb-8 flex justify-between items-center">
                        Evolução de Gastos (BRL)
                        <Info className="w-5 h-5 text-gray-300 cursor-help" />
                    </h3>
                    <div className="h-[350px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={dadosFinOps.comparativo}>
                                <defs>
                                    <linearGradient id="colorTwilio" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="colorGemini" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
                                <XAxis dataKey="mês" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 700 }} dy={10} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12, fontWeight: 700 }} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#fff', borderRadius: '20px', border: 'none', shadow: '0 20px 25px -5px rgb(0 0 0 / 0.1)' }}
                                    itemStyle={{ fontWeight: 900, textTransform: 'uppercase', fontSize: '10px' }}
                                />
                                <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px', fontWeight: 900, textTransform: 'uppercase', fontSize: '10px', letterSpacing: '0.1em' }} />
                                <Area type="monotone" dataKey="twilio" stroke="#10b981" strokeWidth={4} fillOpacity={1} fill="url(#colorTwilio)" name="Twilio (Voz)" />
                                <Area type="monotone" dataKey="gemini" stroke="#6366f1" strokeWidth={4} fillOpacity={1} fill="url(#colorGemini)" name="Gemini (IA)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Gastos por Idoso */}
                <div className="bg-white p-10 rounded-[2.5rem] shadow-xl border border-pink-50 overflow-hidden flex flex-col">
                    <h3 className="text-xl font-black text-gray-900 mb-8 flex justify-between items-center">
                        Consumo detalhado por Idoso
                        <Filter className="w-5 h-5 text-gray-300 pointer" />
                    </h3>
                    <div className="flex-1 overflow-y-auto custom-scrollbar">
                        <table className="w-full text-left">
                            <thead className="sticky top-0 bg-white z-10">
                                <tr className="text-[10px] font-black uppercase text-gray-400 tracking-[0.2em] border-b border-gray-50">
                                    <th className="py-4">Idoso</th>
                                    <th className="py-4">Uso (Min)</th>
                                    <th className="py-4 text-right">Custo Total</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-50">
                                {dadosFinOps.porIdoso.map((item, idx) => (
                                    <tr key={idx} className="group hover:bg-pink-50/20 transition-colors">
                                        <td className="py-5">
                                            <p className="font-bold text-gray-900">{item.nome}</p>
                                            <p className="text-[10px] font-black text-indigo-400 uppercase tracking-widest">{item.tokens.toLocaleString()} tokens</p>
                                        </td>
                                        <td className="py-5">
                                            <div className="flex items-center gap-2">
                                                <div className="w-24 h-2 bg-gray-100 rounded-full overflow-hidden">
                                                    <div className="h-full bg-emerald-500" style={{ width: `${(item.minutos / 500) * 100}%` }}></div>
                                                </div>
                                                <span className="text-xs font-black text-gray-600">{item.minutos}m</span>
                                            </div>
                                        </td>
                                        <td className="py-5 text-right font-black text-pink-600">
                                            R$ {item.custo.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Aviso de Margem */}
            <div className="p-8 bg-indigo-900 rounded-[2.5rem] shadow-2xl shadow-indigo-200 flex flex-col md:flex-row items-center justify-between gap-6 overflow-hidden relative">
                {/* Background Decor */}
                <div className="absolute top-0 right-0 w-64 h-64 bg-white/5 rounded-full -mr-20 -mt-20 blur-3xl"></div>

                <div className="relative z-10 flex items-center gap-6 text-center md:text-left">
                    <div className="p-5 bg-white/10 rounded-3xl backdrop-blur-md">
                        <TrendingUp className="w-10 h-10 text-pink-400" />
                    </div>
                    <div>
                        <h4 className="text-2xl font-black text-white leading-tight">Margem de Contribuição está em 68%</h4>
                        <p className="text-indigo-200 font-medium">Parabéns! Sua eficiência de tokens Gemini melhorou 5% esta semana.</p>
                    </div>
                </div>
                <button className="relative z-10 px-10 py-4 bg-white text-indigo-900 rounded-[1.5rem] font-black shadow-xl hover:scale-105 transition-transform">
                    Otimizar Prompts
                </button>
            </div>
        </div>
    );
}
