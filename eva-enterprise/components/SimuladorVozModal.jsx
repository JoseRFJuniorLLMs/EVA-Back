import React, { useState } from 'react';
import { X, Play, Volume2, Mic2, Heart, Shield, Sparkles, User, Headphones } from 'lucide-react';

export default function SimuladorVozModal({ isOpen, onClose }) {
    const [selectedVoice, setSelectedVoice] = useState('Aoede');
    const [selectedTone, setSelectedTone] = useState('Amigável');
    const [previewText, setPreviewText] = useState('Olá, eu sou a EVA. Estou aqui para cuidar de quem você ama com carinho e atenção.');
    const [isPlaying, setIsPlaying] = useState(false);

    if (!isOpen) return null;

    const voices = [
        { id: 'Puck', name: 'Puck', desc: 'Jovial e entusiasmada', icon: Sparkles, color: 'text-orange-500', bg: 'bg-orange-50' },
        { id: 'Charon', name: 'Charon', desc: 'Séria e profissional', icon: Shield, color: 'text-blue-500', bg: 'bg-blue-50' },
        { id: 'Kore', name: 'Kore', desc: 'Suave e acolhedora', icon: Heart, color: 'text-pink-500', bg: 'bg-pink-50' },
        { id: 'Fenrir', name: 'Fenrir', desc: 'Profunda e autoritária', icon: User, color: 'text-gray-700', bg: 'bg-gray-100' },
        { id: 'Aoede', name: 'Aoede', desc: 'Equilibrada e clara', icon: Headphones, color: 'text-purple-500', bg: 'bg-purple-50' },
    ];

    const tones = ['Formal', 'Amigável', 'Maternal', 'Jovial'];

    const handlePlay = () => {
        setIsPlaying(true);
        // Simulação de áudio para preview (Web Speech API como fallback de teste local)
        const utterance = new SpeechSynthesisUtterance(previewText);
        utterance.lang = 'pt-BR';
        utterance.onend = () => setIsPlaying(false);
        window.speechSynthesis.speak(utterance);
    };

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-md z-[120] flex items-center justify-center p-4 animate-in fade-in duration-300">
            <div className="bg-white w-full max-w-4xl rounded-[2.5rem] shadow-2xl overflow-hidden border border-white/20 animate-in zoom-in-95 duration-500 flex flex-col md:flex-row h-[90vh] md:h-auto">

                {/* Lateral Esquerda - Seleção de Voz */}
                <div className="w-full md:w-80 bg-gray-50 border-r border-gray-100 p-8 flex flex-col">
                    <h3 className="text-xl font-black text-gray-900 mb-6 flex items-center gap-2">
                        <Mic2 className="w-6 h-6 text-pink-600" /> Perfis de Voz
                    </h3>

                    <div className="space-y-3 flex-1">
                        {voices.map((voice) => (
                            <button
                                key={voice.id}
                                onClick={() => setSelectedVoice(voice.id)}
                                className={`w-full p-4 rounded-2xl flex items-center gap-4 transition-all ${selectedVoice === voice.id
                                        ? 'bg-white shadow-lg border-2 border-pink-500 scale-[1.02]'
                                        : 'hover:bg-gray-100 border-2 border-transparent text-gray-400'
                                    }`}
                            >
                                <div className={`w-10 h-10 rounded-xl ${voice.bg} ${voice.color} flex items-center justify-center`}>
                                    <voice.icon className="w-5 h-5" />
                                </div>
                                <div className="text-left">
                                    <p className={`font-bold ${selectedVoice === voice.id ? 'text-gray-900' : ''}`}>{voice.name}</p>
                                    <p className="text-[10px] uppercase font-bold tracking-widest">{voice.desc}</p>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Conteúdo Principal */}
                <div className="flex-1 p-8 md:p-12 relative">
                    <button onClick={onClose} className="absolute top-6 right-6 p-2 text-gray-300 hover:text-gray-600 transition-colors">
                        <X className="w-8 h-8" />
                    </button>

                    <div className="h-full flex flex-col justify-between">
                        <div>
                            <span className="px-3 py-1 bg-pink-100 text-pink-600 text-[10px] font-black uppercase rounded-full tracking-widest">Enterprise Preview</span>
                            <h2 className="text-4xl font-black text-gray-900 mt-4 leading-tight">Simulador de Voz da EVA</h2>
                            <p className="text-gray-500 mt-2">Ajuste a personalidade da IA para o melhor conforto do idoso.</p>

                            <div className="mt-10 space-y-8">
                                {/* Tom de Voz */}
                                <div>
                                    <p className="text-sm font-black text-gray-400 uppercase tracking-widest mb-4">Personalidade (Tone)</p>
                                    <div className="flex flex-wrap gap-3">
                                        {tones.map(tone => (
                                            <button
                                                key={tone}
                                                onClick={() => setSelectedTone(tone)}
                                                className={`px-6 py-3 rounded-xl font-bold transition-all ${selectedTone === tone
                                                        ? 'bg-gray-900 text-white shadow-xl'
                                                        : 'bg-white border-2 border-gray-100 text-gray-500 hover:border-pink-200'
                                                    }`}
                                            >
                                                {tone}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                {/* Texto de Preview */}
                                <div>
                                    <p className="text-sm font-black text-gray-400 uppercase tracking-widest mb-4">Texto de Teste</p>
                                    <textarea
                                        rows="3"
                                        className="w-full p-6 bg-pink-50/50 border-2 border-pink-100 rounded-[2rem] text-xl font-medium text-pink-900 focus:outline-none focus:border-pink-400 transition-colors italic"
                                        value={previewText}
                                        onChange={e => setPreviewText(e.target.value)}
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Player / Playback */}
                        <div className="bg-gray-900 p-8 rounded-[2.5rem] mt-8 flex items-center justify-between shadow-2xl">
                            <div className="flex items-center gap-6">
                                <button
                                    onClick={handlePlay}
                                    disabled={isPlaying}
                                    className={`w-20 h-20 rounded-full flex items-center justify-center transition-all ${isPlaying ? 'bg-pink-600 animate-pulse' : 'bg-pink-500 hover:bg-pink-400 scale-110 active:scale-95'
                                        }`}
                                >
                                    <Play className={`w-8 h-8 text-white fill-current ${isPlaying ? 'animate-bounce' : ''}`} />
                                </button>
                                <div>
                                    <p className="text-pink-500 font-black text-xs uppercase tracking-widest">Status da Voz</p>
                                    <h4 className="text-white text-2xl font-bold">{isPlaying ? 'Gerando áudio...' : 'Pronta para Testar'}</h4>
                                </div>
                            </div>

                            <div className="hidden lg:flex items-center gap-4 text-pink-500/30">
                                <Volume2 className="w-6 h-6" />
                                <div className="flex gap-1">
                                    {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
                                        <div key={i} className={`w-1 bg-pink-500/20 rounded-full transition-all duration-300 ${isPlaying ? 'h-8' : 'h-4'}`} style={{ height: isPlaying ? `${Math.random() * 2 + 1}rem` : '1rem' }} />
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
