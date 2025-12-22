import React, { useState } from 'react';
import { UserPlus, CalendarPlus, Edit2, Pill, Users, History, Search, Heart, Mic, PhoneCall } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';
import MedicamentosModal from '../components/MedicamentosModal';
import EquipeCuidadoModal from '../components/EquipeCuidadoModal';
import TimelineModal from '../components/TimelineModal';
import MemoriaAfetivaModal from '../components/MemoriaAfetivaModal';
import IntroVozModal from '../components/IntroVozModal';
import OrquestradorFluxoModal from '../components/OrquestradorFluxoModal';
import LaudoMedicoModal from '../components/LaudoMedicoModal';
import ArvoreGenealogicaModal from '../components/ArvoreGenealogicaModal';
import LegadoDigitalModal from '../components/LegadoDigitalModal';
import SinaisVitaisModal from '../components/SinaisVitaisModal';
import { GitBranch, FileText, Network, Sparkles, Activity } from 'lucide-react';

export default function IdososPage() {
    const { idosos, modalType, setModalType, selectedIdoso, setSelectedIdoso, setFormVoiceData } = useEva(); // Usando contexto global
    const [searchTerm, setSearchTerm] = useState('');

    const filteredIdosos = idosos.filter(i =>
        i.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
        i.telefone.includes(searchTerm)
    );

    const openNovoIdoso = () => {
        setSelectedIdoso(null);
        setFormVoiceData({ nome: '', telefone: '' }); // Limpa rastro da voz anterior
        setModalType('novoIdoso');
    }

    const openEditarIdoso = (idoso) => {
        setSelectedIdoso(idoso);
        setModalType('editarIdoso');
    }

    const openNovoAgendamento = (idoso) => {
        setSelectedIdoso(idoso);
        setModalType('novoAgendamento');
    }

    const openMedicamentos = (idoso) => {
        setSelectedIdoso(idoso);
        setModalType('medicamentos');
    }

    const openEquipe = (idoso) => {
        setSelectedIdoso(idoso);
        setModalType('equipe');
    }

    const openTimeline = (idoso) => {
        setSelectedIdoso(idoso);
        setModalType('timeline');
    }

    const openMemoria = (idoso) => {
        setSelectedIdoso(idoso);
        setModalType('memoria');
    }

    const openIntro = (idoso) => {
        setSelectedIdoso(idoso);
        setModalType('introVoz');
    }

    const openFluxo = (idoso) => {
        setSelectedIdoso(idoso);
        setModalType('fluxoAlerta');
    }

    const openLaudo = (idoso) => {
        setSelectedIdoso(idoso);
        setModalType('laudoMedico');
    }

    const openArvore = (idoso) => {
        setSelectedIdoso(idoso);
        setModalType('arvore');
    }

    const openLegado = (idoso) => {
        setSelectedIdoso(idoso);
        setModalType('legado');
    }

    const openSinais = (idoso) => {
        setSelectedIdoso(idoso);
        setModalType('sinais');
    }

    const { dispararChamadaImediata } = useEva();
    const [callingId, setCallingId] = useState(null);

    const handleLigarAgora = async (idoso) => {
        setCallingId(idoso.id);
        await dispararChamadaImediata(idoso);
        setCallingId(null);
        alert(`Chamada de bem-estar disparada para ${idoso.nome}!`);
    };

    return (
        <div className="p-8">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4 mb-8 bg-white p-6 rounded-2xl shadow-sm border border-pink-50">
                <div className="flex-1 w-full relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Buscar idoso por nome ou telefone..."
                        value={searchTerm}
                        onChange={(e) => setSearchTerm(e.target.value)}
                        className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-100 rounded-2xl focus:outline-none focus:border-pink-400 transition-colors font-medium shadow-inner"
                    />
                </div>
                <button onClick={openNovoIdoso} className="flex items-center gap-3 px-8 py-3 bg-pink-600 text-white rounded-2xl hover:bg-pink-700 shadow-lg shadow-pink-200 font-bold transition-all shrink-0">
                    <UserPlus className="w-6 h-6" />
                    Novo Idoso
                </button>
            </div>

            <div className="bg-white rounded-2xl shadow-lg border border-pink-100 overflow-hidden">
                <table className="w-full text-left">
                    <thead className="bg-pink-50 text-pink-700 uppercase text-sm">
                        <tr>
                            <th className="px-6 py-4">Nome</th>
                            <th className="px-6 py-4">Telefone</th>
                            <th className="px-6 py-4">Humor</th>
                            <th className="px-6 py-4">Pendências</th>
                            <th className="px-6 py-4 text-right">Ações</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-pink-50">
                        {filteredIdosos.map(idoso => (
                            <tr key={idoso.id} className="hover:bg-pink-50/50 transition-colors">
                                <td className="px-6 py-4">
                                    <div className="flex items-center gap-4">
                                        <div className="relative">
                                            <img
                                                src={idoso.foto || 'https://via.placeholder.com/150'}
                                                alt={idoso.nome}
                                                className="w-12 h-12 rounded-full object-cover border-2 border-pink-100 shadow-sm"
                                            />
                                            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-white rounded-full"></div>
                                        </div>
                                        <span className="font-bold text-gray-800">{idoso.nome}</span>
                                    </div>
                                </td>
                                <td className="px-6 py-4 text-gray-600">{idoso.telefone}</td>
                                <td className="px-6 py-4">
                                    <div className="flex items-center gap-2">
                                        {idoso.sentimento === 'feliz' && <span title="Feliz" className="text-xl">😊</span>}
                                        {idoso.sentimento === 'neutro' && <span title="Neutro" className="text-xl">😐</span>}
                                        {idoso.sentimento === 'triste' && <span title="Triste" className="text-xl">😢</span>}
                                        {idoso.sentimento === 'ansioso' && <span title="Ansioso" className="text-xl">😰</span>}
                                        <span className="text-[10px] font-bold uppercase text-gray-400 tracking-wider font-mono">{idoso.sentimento}</span>
                                    </div>
                                </td>
                                <td className="px-6 py-4">
                                    <span className="bg-pink-100 text-pink-800 px-3 py-1 rounded-full text-xs font-bold">
                                        {idoso.agendamentos_pendentes || 0}
                                    </span>
                                </td>
                                <td className="px-6 py-4 text-right space-x-4">
                                    <button onClick={() => openTimeline(idoso)} className="text-pink-600 hover:text-pink-800" title="Linha do Tempo 360º">
                                        <History className="w-5 h-5 inline mr-1" /> Timeline
                                    </button>
                                    <button onClick={() => openMemoria(idoso)} className="text-pink-600 hover:text-pink-800" title="Memória Afetiva">
                                        <Heart className="w-5 h-5 inline mr-1" /> Memória
                                    </button>
                                    <button onClick={() => openIntro(idoso)} className="text-pink-600 hover:text-pink-800" title="Intro de Voz Familiar">
                                        <Mic className="w-5 h-5 inline mr-1" /> Intro
                                    </button>
                                    <button onClick={() => openArvore(idoso)} className="text-pink-600 hover:text-pink-800" title="Árvore Genealógica">
                                        <Network className="w-5 h-5 inline mr-1" /> Família
                                    </button>
                                    <button
                                        onClick={() => handleLigarAgora(idoso)}
                                        className={`${callingId === idoso.id ? 'text-green-600 animate-pulse' : 'text-pink-600 hover:text-green-600'} transition-colors`}
                                        disabled={callingId !== null}
                                        title="Ligar Agora (Wellness Check)"
                                    >
                                        <PhoneCall className="w-5 h-5 inline mr-1" /> {callingId === idoso.id ? 'Chamando...' : 'Ligar'}
                                    </button>
                                    <button onClick={() => openEquipe(idoso)} className="text-pink-600 hover:text-pink-800" title="Equipe de Cuidado">
                                        <Users className="w-5 h-5 inline mr-1" /> Equipe
                                    </button>
                                    <button onClick={() => openFluxo(idoso)} className="text-pink-600 hover:text-pink-800" title="Orquestrador de Fluxos">
                                        <GitBranch className="w-5 h-5 inline mr-1" /> Fluxo
                                    </button>
                                    <button onClick={() => openLegado(idoso)} className="text-indigo-600 hover:text-indigo-800" title="Legado Digital (Cápsula do Tempo)">
                                        <Sparkles className="w-5 h-5 inline mr-1" /> Legado
                                    </button>
                                    <button onClick={() => openSinais(idoso)} className="text-emerald-600 hover:text-emerald-800" title="Sinais Vitais">
                                        <Activity className="w-5 h-5 inline mr-1" /> Saúde
                                    </button>
                                    <button onClick={() => openLaudo(idoso)} className="text-pink-600 hover:text-pink-800" title="Gerar Laudo Médico (PDF)">
                                        <FileText className="w-5 h-5 inline mr-1" /> Laudo
                                    </button>
                                    <button onClick={() => openMedicamentos(idoso)} className="text-pink-600 hover:text-pink-800" title="Medicamentos">
                                        <Pill className="w-5 h-5 inline mr-1" /> Remédios
                                    </button>
                                    <button onClick={() => openNovoAgendamento(idoso)} className="text-pink-600 hover:text-pink-800" title="Agendar Ligação">
                                        <CalendarPlus className="w-5 h-5 inline mr-1" /> Agendar
                                    </button>
                                    <button onClick={() => openEditarIdoso(idoso)} className="text-pink-600 hover:text-pink-800" title="Editar Idoso">
                                        <Edit2 className="w-5 h-5 inline" />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <MedicamentosModal
                isOpen={modalType === 'medicamentos'}
                onClose={() => setModalType(null)}
                idoso={selectedIdoso}
            />

            <EquipeCuidadoModal
                isOpen={modalType === 'equipe'}
                onClose={() => setModalType(null)}
                idoso={selectedIdoso}
            />

            <TimelineModal
                isOpen={modalType === 'timeline'}
                onClose={() => setModalType(null)}
                idoso={selectedIdoso}
            />

            <MemoriaAfetivaModal
                isOpen={modalType === 'memoria'}
                onClose={() => setModalType(null)}
                idoso={selectedIdoso}
            />

            <IntroVozModal
                isOpen={modalType === 'introVoz'}
                onClose={() => setModalType(null)}
                idoso={selectedIdoso}
            />

            <OrquestradorFluxoModal
                isOpen={modalType === 'fluxoAlerta'}
                onClose={() => setModalType(null)}
                idoso={selectedIdoso}
            />

            <LaudoMedicoModal
                isOpen={modalType === 'laudoMedico'}
                onClose={() => setModalType(null)}
                idoso={selectedIdoso}
            />

            <ArvoreGenealogicaModal
                isOpen={modalType === 'arvore'}
                onClose={() => setModalType(null)}
                idoso={selectedIdoso}
            />

            <LegadoDigitalModal
                isOpen={modalType === 'legado'}
                onClose={() => setModalType(null)}
                idoso={selectedIdoso}
            />

            <SinaisVitaisModal
                isOpen={modalType === 'sinais'}
                onClose={() => setModalType(null)}
                idoso={selectedIdoso}
            />
        </div>
    );
}
