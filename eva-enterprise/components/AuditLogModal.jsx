import React from 'react';
import { X, ClipboardList, Shield, Search, Filter } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';

export default function AuditLogModal({ isOpen, onClose }) {
    const { auditLogs } = useEva();

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-[120] flex items-center justify-center p-4 animate-in fade-in duration-300">
            <div className="bg-white w-full max-w-5xl rounded-[2.5rem] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-500 h-[85vh] flex flex-col">

                {/* Header */}
                <div className="p-8 border-b bg-gray-50 flex justify-between items-center">
                    <div>
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-indigo-100 text-indigo-600 rounded-xl">
                                <ClipboardList className="w-6 h-6" />
                            </div>
                            <h2 className="text-2xl font-black text-gray-900">Log de Auditoria</h2>
                        </div>
                        <p className="text-sm text-gray-500 mt-1">Histórico de alterações e eventos críticos do sistema Enterprise.</p>
                    </div>
                    <button onClick={onClose} className="p-2 text-gray-300 hover:text-gray-600 transition-colors">
                        <X className="w-8 h-8" />
                    </button>
                </div>

                {/* Filters / Search */}
                <div className="p-6 border-b flex gap-4 bg-white">
                    <div className="flex-1 relative">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Buscar logs por usuário, ação ou recurso..."
                            className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-100 rounded-2xl focus:outline-none focus:border-indigo-400 transition-colors font-medium"
                        />
                    </div>
                    <button className="flex items-center gap-2 px-6 py-3 bg-white border border-gray-200 rounded-2xl font-bold text-gray-600 hover:bg-gray-50 transition-colors">
                        <Filter className="w-5 h-5" /> Filtrar
                    </button>
                </div>

                {/* Table Content */}
                <div className="flex-1 overflow-y-auto">
                    <table className="w-full text-left border-collapse">
                        <thead className="sticky top-0 bg-gray-50 text-indigo-900 text-xs font-black uppercase tracking-widest border-b">
                            <tr>
                                <th className="px-8 py-5">Data/Hora</th>
                                <th className="px-8 py-5">Usuário</th>
                                <th className="px-8 py-5">Ação</th>
                                <th className="px-8 py-5">Recurso</th>
                                <th className="px-8 py-5">Detalhes</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-50">
                            {auditLogs.map((log) => (
                                <tr key={log.id} className="hover:bg-indigo-50/30 transition-colors">
                                    <td className="px-8 py-5 text-sm font-bold text-gray-400 font-mono">
                                        {log.data}
                                    </td>
                                    <td className="px-8 py-5">
                                        <div className="flex items-center gap-2">
                                            <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center text-xs font-bold text-indigo-600">
                                                {log.usuario.charAt(0).toUpperCase()}
                                            </div>
                                            <span className="text-sm font-semibold text-gray-700">{log.usuario}</span>
                                        </div>
                                    </td>
                                    <td className="px-8 py-5">
                                        <span className={`px-3 py-1 rounded-lg text-[10px] font-black tracking-widest uppercase ${log.acao.includes('ALERTA') ? 'bg-red-100 text-red-600' :
                                                log.acao.includes('DEPLOY') ? 'bg-green-100 text-green-600' :
                                                    'bg-indigo-100 text-indigo-600'
                                            }`}>
                                            {log.acao.replace('_', ' ')}
                                        </span>
                                    </td>
                                    <td className="px-8 py-5">
                                        <span className="text-sm font-mono text-gray-600 bg-gray-100 px-2 py-1 rounded border border-gray-200">
                                            {log.recurso}
                                        </span>
                                    </td>
                                    <td className="px-8 py-5">
                                        <p className="text-sm text-gray-600 leading-relaxed italic">
                                            "{log.detalhes}"
                                        </p>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>

                {/* Footer / Stats */}
                <div className="p-6 bg-gray-50 border-t flex justify-between items-center text-sm font-medium text-gray-400">
                    <div className="flex items-center gap-2">
                        <Shield className="w-4 h-4" />
                        <span>Auditoria Certificada Enterprise</span>
                    </div>
                    <span>{auditLogs.length} eventos registrados nas últimas 24h</span>
                </div>
            </div>
        </div>
    );
}
