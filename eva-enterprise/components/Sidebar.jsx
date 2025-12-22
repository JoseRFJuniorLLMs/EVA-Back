import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';
import {
    Users, Calendar, Home, Bell, Settings, History,
    BarChart2, DollarSign, PieChart, Brain,
    ChevronLeft, ChevronRight, CreditCard, Coins
} from 'lucide-react';
import { useEva } from '../contexts/EvaContext';
import { useTranslation } from 'react-i18next';

export default function Sidebar() {
    const { alertas } = useEva();
    const { t } = useTranslation();
    const [isCollapsed, setIsCollapsed] = useState(false);

    const navItems = [
        { path: '/', icon: Home, label: t('dashboard') },
        { path: '/idosos', icon: Users, label: t('idosos') },
        { path: '/agendamentos', icon: Calendar, label: t('agendamentos') },
        { path: '/alertas', icon: Bell, label: t('alertas'), badge: alertas.length > 0 ? alertas.length : null },
        { path: '/historico', icon: History, label: t('historico') },
        { path: '/pagamentos', icon: DollarSign, label: t('pagamentos') },
        { path: '/finops', icon: PieChart, label: t('finops') },
        { path: '/relatorios', icon: BarChart2, label: t('relatorios') },
        { path: '/psicologia', icon: Brain, label: 'Psicologia IA', badge: 'PRO' },
        { path: '/planos', icon: Coins, label: t('assinatura'), badge: 'NOVO' },
        { path: '/config', icon: Settings, label: t('configuracoes') },
    ];

    return (
        <div className={`z-40 relative bg-white border-r border-pink-100 min-h-screen hidden md:block transition-all duration-300 ease-in-out ${isCollapsed ? 'w-20' : 'w-64'}`}>
            {/* Botão de Toggle */}
            <button
                onClick={() => setIsCollapsed(!isCollapsed)}
                className="absolute -right-3 top-12 bg-pink-500 text-white border-2 border-white rounded-full p-1 shadow-lg hover:bg-pink-600 transition-all z-50 hover:scale-110 active:scale-95 flex items-center justify-center cursor-pointer"
            >
                {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
            </button>

            <nav className={`p-4 space-y-2 ${isCollapsed ? 'flex flex-col items-center' : ''}`}>
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        title={isCollapsed ? item.label : ''}
                        className={({ isActive }) =>
                            `relative flex items-center gap-3 px-4 py-3 rounded-xl transition-colors font-medium whitespace-nowrap overflow-hidden ${isActive
                                ? 'bg-pink-50 text-pink-600'
                                : 'text-gray-600 hover:bg-gray-50 hover:text-pink-600'
                            } ${isCollapsed ? 'justify-center w-12' : 'w-full'}`
                        }
                    >
                        <item.icon className="w-5 h-5 shrink-0" />
                        {!isCollapsed && (
                            <>
                                <span className="animate-in fade-in duration-300">{item.label}</span>
                                {item.badge && (
                                    <span className="ml-auto bg-red-500 text-white text-[10px] font-black rounded-full h-5 px-1.5 flex items-center justify-center min-w-[20px]">
                                        {item.badge}
                                    </span>
                                )}
                            </>
                        )}
                        {isCollapsed && item.badge && (
                            <div className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full border border-white" />
                        )}
                    </NavLink>
                ))}
            </nav>
        </div>
    );
}
