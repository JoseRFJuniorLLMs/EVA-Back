import { Users, Calendar, AlertCircle, ArrowRight, Activity, Heart, Thermometer, Droplets } from 'lucide-react';
import { Link } from 'react-router-dom';
import { useEva } from '../contexts/EvaContext';
import { useTranslation } from 'react-i18next';

export default function DashboardPage() {
    const { idosos, agendamentos, alertas, loading } = useEva();
    const { t } = useTranslation();

    if (loading) {
        return <div className="text-center py-8 text-pink-600">{t('loading')}</div>;
    }

    return (
        <div className="p-8">
            <h2 className="text-3xl font-bold text-gray-800 mb-8">{t('overview')}</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-10">
                <div className="bg-pink-50 rounded-2xl shadow-lg p-8 border border-pink-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-lg text-gray-700">{t('registeredElders')}</p>
                            <p className="text-4xl font-bold text-pink-600 mt-3">{idosos.length}</p>
                        </div>
                        <Users className="w-16 h-16 text-pink-500" />
                    </div>
                </div>
                <div className="bg-pink-50 rounded-2xl shadow-lg p-8 border border-pink-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-lg text-gray-700">{t('todaysAppointments')}</p>
                            <p className="text-4xl font-bold text-pink-600 mt-3">
                                {agendamentos.filter(a => a.status === 'pendente').length}
                            </p>
                        </div>
                        <Calendar className="w-16 h-16 text-pink-500" />
                    </div>
                </div>
                <div className="bg-pink-50 rounded-2xl shadow-lg p-8 border border-pink-200">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-lg text-gray-700">{t('activeAlerts')}</p>
                            <p className="text-4xl font-bold text-red-600 mt-3">{alertas.length}</p>
                        </div>
                        <AlertCircle className="w-16 h-16 text-red-500" />
                    </div>
                </div>
            </div>

            <div className="bg-white rounded-[2.5rem] shadow-xl p-10 border border-gray-100">
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-pink-100 rounded-2xl text-pink-600">
                            <Users className="w-8 h-8" />
                        </div>
                        <div>
                            <h3 className="text-2xl font-black text-gray-900 leading-tight">{t('familyEmotionalHealth')}</h3>
                            <p className="text-gray-500 font-medium">{t('summaryMood')}</p>
                        </div>
                    </div>
                    <Link to="/psicologia" className="flex items-center gap-2 text-pink-600 font-bold hover:underline">
                        Ver Análise da Psicóloga <ArrowRight className="w-5 h-5" />
                    </Link>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                    <div className="p-6 bg-green-50 rounded-[2rem] border border-green-100 flex flex-col items-center">
                        <span className="text-4xl mb-3">😊</span>
                        <p className="text-green-800 font-black text-2xl">{idosos.filter(i => i.sentimento === 'feliz').length}</p>
                        <p className="text-green-600 text-xs font-bold uppercase tracking-widest mt-1">Estáveis e Felizes</p>
                    </div>
                    <div className="p-6 bg-gray-50 rounded-[2rem] border border-gray-100 flex flex-col items-center">
                        <span className="text-4xl mb-3">😐</span>
                        <p className="text-gray-800 font-black text-2xl">{idosos.filter(i => i.sentimento === 'neutro').length}</p>
                        <p className="text-gray-600 text-xs font-bold uppercase tracking-widest mt-1">Neutros / Normal</p>
                    </div>
                    <div className="p-6 bg-amber-50 rounded-[2rem] border border-amber-100 flex flex-col items-center">
                        <span className="text-4xl mb-3">😰</span>
                        <p className="text-amber-800 font-black text-2xl">{idosos.filter(i => i.sentimento === 'ansioso').length}</p>
                        <p className="text-amber-600 text-xs font-bold uppercase tracking-widest mt-1">Leve Ansiedade</p>
                    </div>
                    <div className="p-6 bg-red-50 rounded-[2rem] border border-red-100 flex flex-col items-center">
                        <span className="text-4xl mb-3">😢</span>
                        <p className="text-red-800 font-black text-2xl">{idosos.filter(i => i.sentimento === 'triste').length}</p>
                        <p className="text-red-600 text-xs font-bold uppercase tracking-widest mt-1">Precisam de Carinho</p>
                    </div>
                </div>
            </div>
            <div className="bg-white rounded-[2.5rem] shadow-xl p-10 border border-gray-100 mt-10">
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-emerald-100 rounded-2xl text-emerald-600">
                            <Activity className="w-8 h-8" />
                        </div>
                        <div>
                            <h3 className="text-2xl font-black text-gray-900 leading-tight">Últimos Sinais Vitais</h3>
                            <p className="text-gray-500 font-medium">Capturados na última conversa do idoso</p>
                        </div>
                    </div>
                    <Link to="/idosos" className="flex items-center gap-2 text-emerald-600 font-bold hover:underline text-sm uppercase tracking-widest">
                        Gerenciar Saúde <ArrowRight className="w-5 h-5" />
                    </Link>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="p-6 bg-red-50 rounded-[2rem] border border-red-100 flex items-center justify-between group hover:scale-105 transition-all">
                        <div className="flex items-center gap-4">
                            <div className="p-3 bg-red-100 text-red-600 rounded-2xl"><Heart className="w-6 h-6" /></div>
                            <div>
                                <p className="text-gray-500 text-xs font-black uppercase tracking-widest">Pressão</p>
                                <p className="text-2xl font-black text-red-700">12/8</p>
                            </div>
                        </div>
                        <div className="text-right">
                            <span className="text-[10px] font-bold text-red-400">Normal</span>
                        </div>
                    </div>

                    <div className="p-6 bg-blue-50 rounded-[2rem] border border-blue-100 flex items-center justify-between group hover:scale-105 transition-all">
                        <div className="flex items-center gap-4">
                            <div className="p-3 bg-blue-100 text-blue-600 rounded-2xl"><Droplets className="w-6 h-6" /></div>
                            <div>
                                <p className="text-gray-500 text-xs font-black uppercase tracking-widest">Glicose</p>
                                <p className="text-2xl font-black text-blue-700">95 <span className="text-xs">mg/dL</span></p>
                            </div>
                        </div>
                        <div className="text-right">
                            <span className="text-[10px] font-bold text-blue-400">Estável</span>
                        </div>
                    </div>

                    <div className="p-6 bg-amber-50 rounded-[2rem] border border-amber-100 flex items-center justify-between group hover:scale-105 transition-all">
                        <div className="flex items-center gap-4">
                            <div className="p-3 bg-amber-100 text-amber-600 rounded-2xl"><Thermometer className="w-6 h-6" /></div>
                            <div>
                                <p className="text-gray-500 text-xs font-black uppercase tracking-widest">Temperatura</p>
                                <p className="text-2xl font-black text-amber-700">36.6 <span className="text-xs">°C</span></p>
                            </div>
                        </div>
                        <div className="text-right">
                            <span className="text-[10px] font-bold text-amber-400">Normal</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
