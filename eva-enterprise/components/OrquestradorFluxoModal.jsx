import React from 'react';
import { X, GitBranch, Bell, MessageSquare, PhoneMissed, ArrowRight, ShieldCheck, Clock, Settings2 } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';

export default function OrquestradorFluxoModal({ isOpen, onClose, idoso }) {
    const { fluxosAlerta } = useEva();

    if (!isOpen || !idoso) return null;

    const fluxo = fluxosAlerta.find(f => f.idoso_id === idoso.id) || {
        nome: 'Nenhum protocolo ativo',
        etapas: []
    };

    const getActionIcon = (acao) => {
        switch (acao) {
            case 'RETRY': return <PhoneMissed className="w-5 h-5 text-pink-600" />;
            case 'NOTIFY_WA': return <MessageSquare className="w-5 h-5 text-green-500" />;
            case 'NOTIFY_SMS': return <Bell className="w-5 h-5 text-amber-500" />;
            default: return <Settings2 className="w-5 h-5 text-gray-400" />;
        }
    }

    const getActionTitle = (acao) => {
        switch (acao) {
            case 'RETRY': return 'Tentar novamente';
            case 'NOTIFY_WA': return 'Notificar WhatsApp';
            case 'NOTIFY_SMS': return 'Notificar SMS';
            default: return 'Ação Desconhecida';
        }
    }

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[150] flex items-center justify-center p-4">
            <div className="bg-white w-full max-w-3xl rounded-[2.5rem] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
                <div className="p-5 border-b border-gray-100 flex justify-between items-center bg-gradient-to-r from-pink-50 to-white">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-pink-100 rounded-2xl text-pink-600">
                            <GitBranch className="w-6 h-6" />
                        </div>
                        <div>
                            <h3 className="text-xl font-black text-gray-900 leading-tight">Orquestrador de Fluxos</h3>
                            <p className="text-sm text-gray-500 font-medium">Protocolo de Emergência para {idoso.nome}</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                        <X className="w-6 h-6 text-gray-400" />
                    </button>
                </div>

                <div className="p-6">
                    <div className="mb-6 flex items-center justify-between">
                        <div className="flex items-center gap-2 px-4 py-2 bg-pink-50 rounded-xl border border-pink-100">
                            <ShieldCheck className="w-5 h-5 text-pink-600" />
                            <span className="text-sm font-black text-pink-800 uppercase tracking-widest">{fluxo.nome}</span>
                        </div>
                        <button className="text-pink-600 font-bold hover:underline text-sm uppercase tracking-widest">Editar Fluxo</button>
                    </div>

                    <div className="relative flex flex-col gap-8 items-center">
                        {/* Linha vertical conectora */}
                        <div className="absolute top-0 bottom-0 w-1 bg-gradient-to-b from-pink-200 via-pink-100 to-transparent left-1/2 -ml-0.5 mt-4"></div>

                        {/* Etapa 0: A Chamada Falhou */}
                        <div className="relative z-10 w-full flex flex-col items-center">
                            <div className="bg-red-500 text-white p-3 rounded-2xl shadow-lg ring-4 ring-red-50 mb-2">
                                <PhoneMissed className="w-6 h-6" />
                            </div>
                            <span className="text-[10px] font-black text-red-500 uppercase tracking-[0.2em]">Idoso não atendeu</span>
                        </div>

                        {fluxo.etapas.map((etapa, idx) => (
                            <React.Fragment key={etapa.id}>
                                <div className="relative z-10 w-full flex items-center justify-center gap-8 group">
                                    <div className="flex-1 text-right invisible md:visible">
                                        <span className="text-[10px] font-black text-gray-400 uppercase tracking-widest block mb-1">Pausa</span>
                                        <div className="flex items-center justify-end gap-1 text-pink-600 font-bold">
                                            <Clock className="w-4 h-4" /> {etapa.delay} min
                                        </div>
                                    </div>

                                    <div className="p-4 bg-white border-2 border-pink-100 rounded-3xl shadow-xl w-64 group-hover:border-pink-500 transition-all scale-100 group-hover:scale-105">
                                        <div className="flex items-center gap-4 mb-1">
                                            <div className="p-2 bg-gray-50 rounded-xl group-hover:bg-pink-50 transition-colors">
                                                {getActionIcon(etapa.acao)}
                                            </div>
                                            <div>
                                                <h4 className="font-bold text-gray-900 leading-tight">{getActionTitle(etapa.acao)}</h4>
                                                <span className={`text-[10px] font-black uppercase tracking-widest ${etapa.status === 'Ativo' ? 'text-green-500' : 'text-gray-400'}`}>
                                                    {etapa.status}
                                                </span>
                                            </div>
                                        </div>
                                        <p className="text-xs text-gray-500 font-medium">
                                            {etapa.acao === 'RETRY'
                                                ? `Serão realizadas mais ${etapa.vezes} tentativas de voz.`
                                                : `Notificação enviada para ${etapa.contato}.`}
                                        </p>
                                    </div>

                                    <div className="flex-1 text-left">
                                        <div className="bg-pink-50 text-pink-600 w-8 h-8 rounded-full flex items-center justify-center font-black text-xs ring-4 ring-pink-100">
                                            {idx + 1}
                                        </div>
                                    </div>
                                </div>
                            </React.Fragment>
                        ))}

                        <div className="relative z-10 pt-4">
                            <button className="flex items-center gap-2 px-4 py-2 bg-gray-50 text-gray-400 border-2 border-dashed border-gray-200 rounded-3xl font-black text-xs uppercase tracking-widest hover:bg-pink-50 hover:border-pink-200 hover:text-pink-600 transition-all">
                                <ArrowRight className="w-4 h-4 rotate-90" />
                                Adicionar Etapa de Segurança
                            </button>
                        </div>
                    </div>
                </div>

                <div className="p-4 bg-gray-50 text-center border-t border-gray-100 italic text-gray-400 text-xs">
                    O orquestrador automatiza o protocolo de segurança da EVA Enterprise, garantindo que nenhum alerta seja perdido.
                </div>
            </div>
        </div>
    );
}
