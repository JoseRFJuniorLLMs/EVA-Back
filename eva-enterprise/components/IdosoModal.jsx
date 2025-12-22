import React, { useState, useEffect } from 'react';
import { X, Sparkles } from 'lucide-react'; // Sparkles para o efeito visual da IA
import { useEva } from '../contexts/EvaContext';

export default function IdosoModal({ isOpen, onClose, idosoToEdit = null }) {
    const { carregarDashboard, formVoiceData } = useEva(); // Consumindo os dados da EVA

    const [formIdoso, setFormIdoso] = useState({
        nome: '', telefone: '', data_nascimento: '', endereco: '',
        condicoes_medicas: '', medicamentos_regulares: '',
        limitacoes_auditivas: false, ambiente_ruidoso: false, ganho_audio_entrada: 0,
        foto: ''
    });

    // 1. Efeito para preenchimento automático via VOZ (EVA)
    useEffect(() => {
        if (isOpen && (formVoiceData.nome || formVoiceData.telefone)) {
            setFormIdoso(prev => ({
                ...prev,
                nome: formVoiceData.nome || prev.nome,
                telefone: formVoiceData.telefone || prev.telefone
            }));
        }
    }, [formVoiceData, isOpen]);

    // 2. Efeito original para edição ou reset
    useEffect(() => {
        if (idosoToEdit) {
            setFormIdoso(idosoToEdit);
        } else {
            setFormIdoso({
                nome: '', telefone: '', data_nascimento: '', endereco: '',
                condicoes_medicas: '', medicamentos_regulares: '',
                limitacoes_auditivas: false, ambiente_ruidoso: false, ganho_audio_entrada: 0,
                foto: ''
            });
        }
    }, [idosoToEdit, isOpen]);

    const salvarIdoso = () => {
        console.log('Salvando idoso:', formIdoso);
        // Aqui você integraria com sua API ou Firebase
        carregarDashboard();
        onClose();
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4 backdrop-blur-sm">
            <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-screen overflow-y-auto border border-pink-200 animate-in zoom-in duration-300">
                <div className="p-8">
                    <div className="flex justify-between items-center mb-8">
                        <div>
                            <h3 className="text-2xl font-bold text-pink-700 flex items-center gap-2">
                                {idosoToEdit ? 'Editar Idoso' : 'Novo Idoso'}
                                {(formVoiceData.nome || formVoiceData.telefone) && (
                                    <span className="flex items-center gap-1 text-xs bg-green-100 text-green-600 px-2 py-1 rounded-full animate-pulse">
                                        <Sparkles className="w-3 h-3" /> EVA Preenchendo...
                                    </span>
                                )}
                            </h3>
                        </div>
                        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                            <X className="w-8 h-8" />
                        </button>
                    </div>

                    <div className="space-y-6">
                        {/* Foto do Idoso */}
                        <div className="flex flex-col items-center mb-6">
                            <div className="relative group">
                                <img
                                    src={formIdoso.foto || 'https://via.placeholder.com/150'}
                                    alt="Preview"
                                    className="w-32 h-32 rounded-full object-cover border-4 border-pink-100 shadow-lg group-hover:border-pink-300 transition-all"
                                />
                                <div className="mt-4">
                                    <input
                                        type="text"
                                        placeholder="URL da Foto do Idoso"
                                        value={formIdoso.foto}
                                        onChange={e => setFormIdoso({ ...formIdoso, foto: e.target.value })}
                                        className="text-xs w-full px-3 py-2 border-2 border-pink-50 rounded-lg focus:outline-none focus:border-pink-300 text-center font-medium"
                                    />
                                    <p className="text-[10px] text-gray-400 mt-1 text-center">Insira uma URL de imagem (ex: Unsplash/Imgur)</p>
                                </div>
                            </div>
                        </div>

                        {/* Campo Nome com destaque se vier da voz */}
                        <div className="relative">
                            <input
                                type="text"
                                placeholder="Nome completo"
                                value={formIdoso.nome}
                                onChange={e => setFormIdoso({ ...formIdoso, nome: e.target.value })}
                                className={`w-full px-5 py-3 text-lg border-2 rounded-xl focus:ring-4 outline-none transition-all ${formVoiceData.nome ? 'border-green-300 bg-green-50/30' : 'border-pink-200 focus:border-pink-500 focus:ring-pink-100'}`}
                            />
                        </div>

                        {/* Campo Telefone */}
                        <input
                            type="tel"
                            placeholder="Telefone (+codigo do país)"
                            value={formIdoso.telefone}
                            onChange={e => setFormIdoso({ ...formIdoso, telefone: e.target.value })}
                            className={`w-full px-5 py-3 text-lg border-2 rounded-xl focus:ring-4 outline-none transition-all ${formVoiceData.telefone ? 'border-green-300 bg-green-50/30' : 'border-pink-200 focus:border-pink-500 focus:ring-pink-100'}`}
                        />

                        <input type="date" value={formIdoso.data_nascimento} onChange={e => setFormIdoso({ ...formIdoso, data_nascimento: e.target.value })} className="w-full px-5 py-3 text-lg border-2 border-pink-200 rounded-xl focus:border-pink-500 focus:ring-4 focus:ring-pink-100" />
                        <input type="text" placeholder="Endereço completo" value={formIdoso.endereco} onChange={e => setFormIdoso({ ...formIdoso, endereco: e.target.value })} className="w-full px-5 py-3 text-lg border-2 border-pink-200 rounded-xl focus:border-pink-500 focus:ring-4 focus:ring-pink-100" />
                        <textarea placeholder="Condições médicas conhecidas" value={formIdoso.condicoes_medicas} onChange={e => setFormIdoso({ ...formIdoso, condicoes_medicas: e.target.value })} className="w-full px-5 py-3 text-lg border-2 border-pink-200 rounded-xl focus:border-pink-500 focus:ring-4 focus:ring-pink-100" rows="4" />
                        <textarea placeholder="Medicamentos que toma regularmente" value={formIdoso.medicamentos_regulares} onChange={e => setFormIdoso({ ...formIdoso, medicamentos_regulares: e.target.value })} className="w-full px-5 py-3 text-lg border-2 border-pink-200 rounded-xl focus:border-pink-500 focus:ring-4 focus:ring-pink-100" rows="4" />

                        <div className="space-y-4">
                            <label className="flex items-center gap-4 text-lg">
                                <input type="checkbox" checked={formIdoso.limitacoes_auditivas} onChange={e => setFormIdoso({ ...formIdoso, limitacoes_auditivas: e.target.checked })} className="w-6 h-6 text-pink-600 rounded focus:ring-pink-500" />
                                <span>Tem limitações auditivas</span>
                            </label>
                            <label className="flex items-center gap-4 text-lg">
                                <input type="checkbox" checked={formIdoso.ambiente_ruidoso} onChange={e => setFormIdoso({ ...formIdoso, ambiente_ruidoso: e.target.checked })} className="w-6 h-6 text-pink-600 rounded focus:ring-pink-500" />
                                <span>Vive em ambiente geralmente ruidoso (TV alta, rua, etc.)</span>
                            </label>
                        </div>

                        <div>
                            <label className="block text-lg font-medium mb-3">Ganho de áudio da EVA (volume da voz)</label>
                            <input type="range" min="-10" max="10" step="1" value={formIdoso.ganho_audio_entrada} onChange={e => setFormIdoso({ ...formIdoso, ganho_audio_entrada: parseInt(e.target.value) })} className="w-full h-3 bg-pink-200 rounded-lg appearance-none cursor-pointer" />
                            <div className="text-center mt-3 text-xl font-semibold text-pink-600">
                                {formIdoso.ganho_audio_entrada > 0 ? '+' : ''}{formIdoso.ganho_audio_entrada} dB
                            </div>
                        </div>

                        <button onClick={salvarIdoso} className="w-full py-4 bg-gradient-to-r from-pink-600 to-purple-600 text-white rounded-xl hover:from-pink-700 hover:to-purple-700 font-bold text-xl shadow-lg transform active:scale-[0.98] transition-all">
                            Finalizar Cadastro
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}