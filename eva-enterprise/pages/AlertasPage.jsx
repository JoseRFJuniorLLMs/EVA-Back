import React, { useState } from 'react';
import { Bell, AlertTriangle, Search } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';

export default function AlertasPage() {
    const { alertas } = useEva();
    const [searchTerm, setSearchTerm] = useState('');

    const filteredAlertas = alertas.filter(alerta =>
        alerta.tipo.toLowerCase().includes(searchTerm.toLowerCase()) ||
        alerta.idoso.toLowerCase().includes(searchTerm.toLowerCase()) ||
        alerta.descricao.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="p-8">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4 mb-8 bg-white p-6 rounded-2xl shadow-sm border border-pink-50">
                <h2 className="text-3xl font-bold text-pink-700 shrink-0">Alertas</h2>
                <div className="flex-1 w-full relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Buscar por idoso, tipo ou descrição..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-100 rounded-2xl focus:outline-none focus:border-pink-400 transition-colors font-medium shadow-inner"
                    />
                </div>
            </div>
            <div className="space-y-6">
                {filteredAlertas.length === 0 ? (
                    <div className="text-center py-12 text-gray-500">
                        <Bell className="w-16 h-16 mx-auto text-pink-300 mb-4" />
                        <p className="text-xl">Nenhum alerta encontrado</p>
                        <p className="text-sm mt-2">Tudo tranquilo com os idosos ❤️</p>
                    </div>
                ) : (
                    filteredAlertas.map(alerta => (
                        <div key={alerta.id} className="bg-red-50 border-2 border-red-300 rounded-2xl p-6 flex items-start gap-5 shadow-md">
                            <AlertTriangle className="w-10 h-10 text-red-600 flex-shrink-0" />
                            <div className="flex-1">
                                <p className="text-xl font-bold text-red-900">{alerta.tipo}</p>
                                <p className="text-lg text-red-800 mt-2">{alerta.descricao}</p>
                                <p className="text-sm text-red-600 mt-3">{alerta.data}</p>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
