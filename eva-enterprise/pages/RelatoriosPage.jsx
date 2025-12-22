import React from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
    LineChart, Line, AreaChart, Area, PieChart, Pie, Cell
} from 'recharts';
import { TrendingUp, Users, Clock, Activity, AlertCircle, Phone } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';

export default function RelatoriosPage() {
    const { metricasAnalytics } = useEva();

    if (!metricasAnalytics) {
        return <div className="p-8 text-center text-pink-600 font-bold">Carregando métricas da EVA...</div>;
    }

    const COLORS = ['#db2777', '#9333ea', '#4f46e5', '#0891b2'];

    const StatCard = ({ title, value, subtext, icon: Icon, colorClass }) => (
        <div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-100">
            <div className="flex justify-between items-start mb-4">
                <div className={`p-3 rounded-xl ${colorClass} bg-opacity-10 transition-transform hover:scale-110`}>
                    <Icon className={`w-6 h-6 ${colorClass.replace('bg-', 'text-')}`} />
                </div>
                <TrendingUp className="w-4 h-4 text-green-500" />
            </div>
            <h3 className="text-gray-500 text-sm font-medium">{title}</h3>
            <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
            <p className="text-xs text-gray-400 mt-1">{subtext}</p>
        </div>
    );

    return (
        <div className="p-8 space-y-8">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-3xl font-bold text-gray-800">Enterprise Insights</h2>
                    <p className="text-gray-500">Métricas de adesão e performance da plataforma</p>
                </div>
                <div className="flex gap-2">
                    <span className="px-4 py-2 bg-white border border-gray-200 rounded-xl text-sm font-bold text-gray-600">Últimos 7 dias</span>
                    <button className="px-4 py-2 bg-pink-600 text-white rounded-xl text-sm font-bold hover:bg-pink-700 transition-colors shadow-lg shadow-pink-100">Exportar PDF</button>
                </div>
            </div>

            {/* Top Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Total de Chamadas"
                    value={metricasAnalytics.resumo.totalChamadas}
                    subtext="+12% em relação ao mês anterior"
                    icon={Phone}
                    colorClass="bg-blue-600"
                />
                <StatCard
                    title="Minutos Falados"
                    value={`${metricasAnalytics.resumo.minutosFalados}min`}
                    subtext="Média de 3.2min por chamada"
                    icon={Clock}
                    colorClass="bg-purple-600"
                />
                <StatCard
                    title="Taxa de Sucesso"
                    value={`${metricasAnalytics.resumo.percentualSucesso}%`}
                    subtext="Adesão à medicação confirmada"
                    icon={Activity}
                    colorClass="bg-pink-600"
                />
                <StatCard
                    title="Custo Médio/Min"
                    value={`R$ ${metricasAnalytics.resumo.custoMedio}`}
                    subtext="Otimização de custos ativa"
                    icon={TrendingUp}
                    colorClass="bg-green-600"
                />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Chart 1: Adherence */}
                <div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-100">
                    <h3 className="text-lg font-bold text-gray-800 mb-6 flex items-center gap-2">
                        <Users className="w-5 h-5 text-pink-500" /> Taxa de Adesão por Dia
                    </h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={metricasAnalytics.adesao}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                                <XAxis dataKey="dia" axisLine={false} tickLine={false} tick={{ fill: '#9ca3af', fontSize: 12 }} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#9ca3af', fontSize: 12 }} />
                                <Tooltip
                                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                                    cursor={{ fill: '#fdf2f8' }}
                                />
                                <Legend iconType="circle" wrapperStyle={{ paddingTop: '20px' }} />
                                <Bar dataKey="confirmados" name="Confirmados" fill="#db2777" radius={[4, 4, 0, 0]} barSize={30} />
                                <Bar dataKey="esquecidos" name="Esquecidos" fill="#fbcfe8" radius={[4, 4, 0, 0]} barSize={30} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Chart 2: Latency/Performance */}
                <div className="bg-white p-6 rounded-2xl shadow-lg border border-gray-100">
                    <h3 className="text-lg font-bold text-gray-800 mb-6 flex items-center gap-2">
                        <Activity className="w-5 h-5 text-purple-500" /> Latência da IA (ms)
                    </h3>
                    <div className="h-[300px] w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={metricasAnalytics.qualidade}>
                                <defs>
                                    <linearGradient id="colorLat" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#9333ea" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#9333ea" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                                <XAxis dataKey="hora" axisLine={false} tickLine={false} tick={{ fill: '#9ca3af', fontSize: 12 }} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#9ca3af', fontSize: 12 }} />
                                <Tooltip
                                    contentStyle={{ borderRadius: '16px', border: 'none', boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1)' }}
                                />
                                <Area type="monotone" dataKey="latencia" name="Latência (ms)" stroke="#9333ea" strokeWidth={3} fillOpacity={1} fill="url(#colorLat)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* Callouts */}
            <div className="bg-pink-50 border border-pink-100 p-6 rounded-2xl flex items-start gap-4">
                <AlertCircle className="w-6 h-6 text-pink-600 flex-shrink-0 mt-1" />
                <div>
                    <h4 className="font-bold text-pink-900">Insight da Semanal</h4>
                    <p className="text-pink-800 mt-1 text-sm leading-relaxed">
                        A adesão dos idosos atingiu seu pico na **Quinta-feira** (95%). O horário das **18h** apresentou um leve aumento na latência média devido ao alto volume de chamadas simultâneas. Recomendamos revisar a escalabilidade no cluster Sul-1.
                    </p>
                </div>
            </div>
        </div>
    );
}
