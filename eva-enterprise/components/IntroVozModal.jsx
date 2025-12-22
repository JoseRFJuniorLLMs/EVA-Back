import React, { useState, useRef } from 'react';
import { X, Mic, Square, Play, Trash2, Save, Volume2, Music } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';

export default function IntroVozModal({ isOpen, onClose, idoso }) {
    const { idosos, setIdosos } = useEva();
    const [isRecording, setIsRecording] = useState(false);
    const [audioBlob, setAudioBlob] = useState(null);
    const [audioUrl, setAudioUrl] = useState(idoso?.intro_audio || null);
    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);

    if (!isOpen || !idoso) return null;

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorderRef.current = new MediaRecorder(stream);
            audioChunksRef.current = [];

            mediaRecorderRef.current.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorderRef.current.onstop = () => {
                const blob = new Blob(audioChunksRef.current, { type: 'audio/mpeg' });
                const url = URL.createObjectURL(blob);
                setAudioBlob(blob);
                setAudioUrl(url);
            };

            mediaRecorderRef.current.start();
            setIsRecording(true);
        } catch (err) {
            console.error('Erro ao acessar microfone:', err);
            alert('Não foi possível acessar o microfone.');
        }
    };

    const stopRecording = () => {
        if (mediaRecorderRef.current && isRecording) {
            mediaRecorderRef.current.stop();
            setIsRecording(false);
            mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
        }
    };

    const handleSave = () => {
        // Mock save: update global state
        const updatedIdosos = idosos.map(i =>
            i.id === idoso.id ? { ...i, intro_audio: audioUrl } : i
        );
        setIdosos(updatedIdosos);
        onClose();
    };

    const handleDelete = () => {
        setAudioUrl(null);
        setAudioBlob(null);
    };

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[150] flex items-center justify-center p-4">
            <div className="bg-white w-full max-w-lg rounded-[2.5rem] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
                <div className="p-8 border-b border-gray-100 flex justify-between items-center bg-gradient-to-r from-pink-50 to-white">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-pink-100 rounded-2xl text-pink-600">
                            <Mic className="w-8 h-8" />
                        </div>
                        <div>
                            <h3 className="text-2xl font-black text-gray-900 leading-tight">Intro de Voz Familiar</h3>
                            <p className="text-gray-500 font-medium">Saudação inicial para {idoso.nome}</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                        <X className="w-8 h-8 text-gray-400" />
                    </button>
                </div>

                <div className="p-10 flex flex-col items-center">
                    <div className="mb-8 text-center text-gray-600 font-medium leading-relaxed">
                        Grava uma mensagem curta (ex: "Oi pai, é a Carla. A EVA vai falar com você!") que será tocada no início de cada ligação.
                    </div>

                    {!audioUrl ? (
                        <button
                            onClick={isRecording ? stopRecording : startRecording}
                            className={`w-32 h-32 rounded-full flex items-center justify-center transition-all shadow-xl ${isRecording
                                    ? 'bg-red-500 animate-pulse text-white scale-110 shadow-red-200'
                                    : 'bg-pink-600 text-white hover:bg-pink-700 shadow-pink-100'
                                }`}
                        >
                            {isRecording ? <Square className="w-12 h-12" /> : <Mic className="w-12 h-12" />}
                        </button>
                    ) : (
                        <div className="w-full bg-gray-50 rounded-3xl p-6 border border-gray-100 flex flex-col items-center gap-6 animate-in fade-in zoom-in duration-300">
                            <div className="p-4 bg-white rounded-full shadow-sm text-pink-600">
                                <Volume2 className="w-10 h-10" />
                            </div>
                            <audio src={audioUrl} controls className="w-full" />
                            <div className="flex gap-4 w-full">
                                <button
                                    onClick={handleDelete}
                                    className="flex-1 flex items-center justify-center gap-2 py-3 bg-white border border-red-100 text-red-500 rounded-2xl font-bold hover:bg-red-50 transition-colors"
                                >
                                    <Trash2 className="w-5 h-5" /> Excluir
                                </button>
                                <button
                                    onClick={handleSave}
                                    className="flex-1 flex items-center justify-center gap-2 py-3 bg-pink-600 text-white rounded-2xl font-black shadow-lg shadow-pink-100 hover:bg-pink-700 transition-colors"
                                >
                                    <Save className="w-5 h-5" /> Salvar Áudio
                                </button>
                            </div>
                        </div>
                    )}

                    {isRecording && (
                        <div className="mt-6 flex items-center gap-2 text-red-500 font-black animate-bounce text-sm uppercase tracking-widest">
                            <span className="w-2 h-2 bg-red-500 rounded-full"></span>
                            Gravando...
                        </div>
                    )}

                    {!isRecording && !audioUrl && (
                        <p className="mt-6 text-gray-400 font-black text-[10px] uppercase tracking-[0.2em]">Clique para começar a gravar</p>
                    )}
                </div>

                <div className="p-8 bg-gray-50 text-center border-t border-gray-100 italic text-gray-400 text-xs">
                    Isso ajuda idosos com declínio cognitivo a reconhecerem a chamada como algo seguro e familiar.
                </div>
            </div>
        </div>
    );
}
