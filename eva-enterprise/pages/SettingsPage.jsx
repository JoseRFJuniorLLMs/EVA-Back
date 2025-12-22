import React, { useState } from 'react';
import { Settings, MessageSquare, Terminal, ChevronRight, Plus, Save, X, Mic2, ClipboardList } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';
import SimuladorVozModal from '../components/SimuladorVozModal';
import AuditLogModal from '../components/AuditLogModal';

export default function SettingsPage() {
    const { configuracoes, prompts, funcoes, auditLogs } = useEva();
    const [activePanel, setActivePanel] = useState(null); // 'config', 'prompts', 'funcoes'
    const [searchTerm, setSearchTerm] = useState('');

    const filteredConfig = configuracoes.filter(c =>
        c.chave.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.valor.toLowerCase().includes(searchTerm.toLowerCase()) ||
        c.categoria.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const filteredPrompts = prompts.filter(p =>
        p.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.template.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const filteredFuncoes = funcoes.filter(f =>
        f.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
        f.descricao.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const panels = [
        {
            id: 'config',
            title: 'Configurações Globais',
            description: 'Modelos Gemini, áudio, Twilio e limites do sistema.',
            icon: Settings,
            color: 'text-blue-600',
            bg: 'bg-blue-50',
            count: configuracoes.length
        },
        {
            id: 'prompts',
            title: 'Templates de Prompt',
            description: 'Mustache templates para personalidade e tarefas da EVA.',
            icon: MessageSquare,
            color: 'text-purple-600',
            bg: 'bg-purple-50',
            count: prompts.length
        },
        {
            id: 'funcoes',
            title: 'Definições de Funções',
            description: 'JSON schemas para Function Calling e Handlers.',
            icon: Terminal,
            color: 'text-amber-600',
            bg: 'bg-amber-50',
            count: funcoes.length
        },
        {
            id: 'simulador',
            title: 'Simulador de Voz',
            description: 'Teste tons de voz (Puck, Aoede, etc) e ajuste a clareza para o idoso.',
            icon: Mic2,
            color: 'text-pink-600',
            bg: 'bg-pink-50',
            count: 'Preview'
        },
        {
            id: 'audit',
            title: 'Log de Auditoria',
            description: 'Rastreie alterações em prompts, configurações e alertas de segurança.',
            icon: ClipboardList,
            color: 'text-indigo-600',
            bg: 'bg-indigo-50',
            count: auditLogs.length
        }
    ];

    return (
        <div className="p-8">
            <h2 className="text-3xl font-bold text-gray-800 mb-8">Configurações Enterprise</h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                {panels.map((panel) => (
                    <button
                        key={panel.id}
                        onClick={() => setActivePanel(panel.id)}
                        className="bg-white p-8 rounded-2xl shadow-lg border border-gray-100 text-left transition-all hover:scale-[1.02] hover:shadow-xl group"
                    >
                        <div className={`w-16 h-16 ${panel.bg} ${panel.color} rounded-2xl flex items-center justify-center mb-6 transition-transform group-hover:rotate-6`}>
                            <panel.icon className="w-8 h-8" />
                        </div>
                        <h3 className="text-2xl font-bold text-gray-900 mb-2">{panel.title}</h3>
                        <p className="text-gray-500 mb-6">{panel.description}</p>
                        <div className="flex justify-between items-center text-sm font-medium">
                            <span className={`${panel.color}`}>{panel.count} itens cadastrados</span>
                            <ChevronRight className="w-5 h-5 text-gray-400" />
                        </div>
                    </button>
                ))}
            </div>

            {/* Panel Overlay (Apenas para Config, Prompts e Funções) */}
            {['config', 'prompts', 'funcoes'].includes(activePanel) && (
                <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100] flex justify-end animate-in fade-in duration-300">
                    <div className="w-full max-w-4xl bg-white h-screen shadow-2xl overflow-y-auto animate-in slide-in-from-right duration-500">
                        <div className="p-8">
                            <div className="flex justify-between items-center mb-8 border-b pb-6">
                                <div>
                                    <h3 className="text-2xl font-bold text-gray-900">
                                        {panels.find(p => p.id === activePanel).title}
                                    </h3>
                                    <p className="text-gray-500">Gerenciamento Enterprise de {activePanel}</p>
                                </div>
                                <div className="flex gap-4">
                                    <button className="flex items-center gap-2 px-4 py-2 bg-pink-600 text-white rounded-xl font-bold hover:bg-pink-700 transition-colors">
                                        <Plus className="w-5 h-5" /> Novo
                                    </button>
                                    <button onClick={() => { setActivePanel(null); setSearchTerm(''); }} className="p-2 text-gray-400 hover:bg-gray-100 rounded-full transition-colors">
                                        <X className="w-8 h-8" />
                                    </button>
                                </div>
                            </div>

                            {/* Search Bar inside Panel */}
                            <div className="mb-8 relative">
                                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                                <input
                                    type="text"
                                    placeholder={`Buscar em ${activePanel}...`}
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-100 rounded-2xl focus:outline-none focus:border-pink-400 transition-colors font-medium"
                                />
                            </div>

                            {/* Conteúdo Dinâmico do Painel */}
                            <div className="space-y-6">
                                {activePanel === 'config' && (
                                    <div className="grid grid-cols-1 gap-4">
                                        {filteredConfig.map(c => (
                                            <div key={c.id} className="p-6 bg-gray-50 rounded-2xl border border-gray-200 flex justify-between items-center">
                                                <div>
                                                    <p className="text-sm font-mono text-blue-600">{c.chave}</p>
                                                    <p className="text-lg font-bold text-gray-800 mt-1">{c.valor}</p>
                                                    <span className="text-xs bg-gray-200 px-2 py-0.5 rounded text-gray-600 uppercase">{c.tipo} • {c.categoria}</span>
                                                </div>
                                                <button className="text-pink-600 hover:underline font-bold">Editar</button>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {activePanel === 'prompts' && (
                                    <div className="space-y-6">
                                        {filteredPrompts.map(p => (
                                            <div key={p.id} className="p-6 bg-gray-50 rounded-2xl border border-gray-200">
                                                <div className="flex justify-between items-start mb-4">
                                                    <div>
                                                        <h4 className="text-xl font-bold text-gray-900">{p.nome}</h4>
                                                        <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded font-bold">{p.versao}</span>
                                                    </div>
                                                    <button className="text-pink-600 hover:underline font-bold">Editar</button>
                                                </div>
                                                <pre className="text-sm bg-black text-green-400 p-4 rounded-xl overflow-x-auto font-mono">
                                                    {p.template}
                                                </pre>
                                            </div>
                                        ))}
                                    </div>
                                )}

                                {activePanel === 'funcoes' && (
                                    <div className="space-y-6">
                                        {filteredFuncoes.map(f => (
                                            <div key={f.id} className="p-6 bg-gray-50 rounded-2xl border border-gray-200">
                                                <div className="flex justify-between items-start mb-4">
                                                    <div>
                                                        <h4 className="text-xl font-bold text-gray-900">{f.nome}</h4>
                                                        <p className="text-sm text-gray-500">{f.descricao}</p>
                                                    </div>
                                                    <button className="text-pink-600 hover:underline font-bold">Editar</button>
                                                </div>
                                                <div className="bg-amber-50 p-4 rounded-xl border border-amber-100">
                                                    <span className="text-xs font-bold text-amber-700 uppercase">Tarefa: {f.tipo_tarefa}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            <SimuladorVozModal
                isOpen={activePanel === 'simulador'}
                onClose={() => setActivePanel(null)}
            />

            <AuditLogModal
                isOpen={activePanel === 'audit'}
                onClose={() => setActivePanel(null)}
            />
        </div>
    );
}
