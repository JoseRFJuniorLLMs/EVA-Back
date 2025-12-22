import React, { useState, useEffect, useRef } from 'react';
import { GoogleGenAI, Modality } from '@google/genai';
import { createBlob, decode, decodeAudioData } from '../utils/audioUtils';
import { Mic, MicOff } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';
import { getEvaPrompt, evaTools } from '../configs/evaConfig.js';
import { toast } from 'sonner';
import { GOOGLE_API_KEY } from '../configs/secrets.js';

const VoiceAssistant = () => {
    const { idosos, alertas, agendamentos, setIdosos } = useEva();
    const [isActive, setIsActive] = useState(false);
    const [isReady, setIsReady] = useState(false);
    const [isConnecting, setIsConnecting] = useState(false);

    const inputAudioContextRef = useRef(null);
    const outputAudioContextRef = useRef(null);
    const outputNodeRef = useRef(null);
    const mediaStreamRef = useRef(null);
    const workletNodeRef = useRef(null);
    const nextStartTimeRef = useRef(0);
    const sourcesRef = useRef(new Set());
    const clientRef = useRef(null);
    const sessionRef = useRef(null);
    const activeRef = useRef(false);

    // Referência para o reconhecimento de fala nativo (Speech-to-Text do navegador)
    const recognitionRef = useRef(null);

    useEffect(() => {
        const init = async () => {
            console.log("🔊 EVA: Inicializando AudioContexts...");
            try {
                inputAudioContextRef.current = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
                outputAudioContextRef.current = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 24000 });
                outputNodeRef.current = outputAudioContextRef.current.createGain();
                outputNodeRef.current.connect(outputAudioContextRef.current.destination);

                console.log("🔊 EVA: Carregando AudioWorklet...");
                await inputAudioContextRef.current.audioWorklet.addModule('/audio-processor.js');
                console.log("✅ EVA: AudioWorklet carregado com sucesso!");

                clientRef.current = new GoogleGenAI({
                    apiKey: GOOGLE_API_KEY,
                });

                // Configuração do Speech Recognition NATIVO para legendas (UI apenas)
                if ('webkitSpeechRecognition' in window) {
                    const speechRecognition = new window.webkitSpeechRecognition();
                    speechRecognition.continuous = true;
                    speechRecognition.interimResults = false;
                    speechRecognition.lang = 'pt-BR';

                    speechRecognition.onresult = (event) => {
                        const transcript = event.results[event.results.length - 1][0].transcript;
                        console.log("🗣️ Usuário disse:", transcript);
                        toast.info(`Você: ${transcript}`, {
                            duration: 5000,
                            icon: '🗣️',
                            style: {
                                fontSize: '30px',      // Texto GRANDE
                                padding: '30px',       // Toast GRANDE
                                fontWeight: 'bold',
                                minWidth: '600px',     // Largura EXTRA
                                border: '4px solid #db2777', // Borda Rosa Forte
                                backgroundColor: '#fff',
                                color: '#000'
                            }
                        });
                    };

                    speechRecognition.onerror = (event) => {
                        console.warn("⚠️ Speech API erro:", event.error);
                    };

                    recognitionRef.current = speechRecognition;
                } else {
                    console.warn("⚠️ Navegador não suporta webkitSpeechRecognition (Legendas indisponíveis)");
                }

                setIsReady(true);
            } catch (err) {
                console.error("❌ EVA: Falha crítica na inicialização:", err);
            }
        };
        init();
        return () => stopConversation();
    }, []);

    const handleFunctionCall = (fnCall) => {
        if (fnCall.name === "cadastrarIdoso") {
            const { nome, telefone } = fnCall.args;
            console.log(`🚀 EVA: Executando função cadastrarIdoso para ${nome}`);

            const novoIdoso = {
                id: Date.now(),
                nome: nome,
                telefone: telefone,
                agendamentos_pendentes: 0
            };

            setIdosos(prev => [...prev, novoIdoso]);

            if (sessionRef.current) {
                sessionRef.current.sendFunctionResponse({
                    name: "cadastrarIdoso",
                    response: { content: "OK: Idoso cadastrado com sucesso." }
                }).catch(e => console.error("❌ EVA: Erro ao enviar resposta da função:", e));
            }
        }
    };

    const initSession = async () => {
        console.log("🔌 EVA: Conectando ao Gemini...");
        setIsConnecting(true);
        const promptDinamico = getEvaPrompt({ idosos, alertas, agendamentos });

        try {
            sessionRef.current = await clientRef.current.live.connect({
                model: 'gemini-2.5-flash-native-audio-preview-12-2025',
                config: {
                    tools: evaTools,
                    responseModalities: [Modality.AUDIO],
                    systemInstruction: { parts: [{ text: promptDinamico }] },
                    speechConfig: {
                        voiceConfig: { prebuiltVoiceConfig: { voiceName: 'Aoede' } }
                    },
                },
                callbacks: {
                    onopen: () => {
                        console.log('✅ EVA: Sessão Aberta (WebSocket Connected)');
                        setIsConnecting(false);
                        toast.success("EVA Conectada! Pode falar.", { duration: 3000 });
                    },
                    onmessage: async (message) => {
                        // Transcrição da IA (se disponível no retorno)
                        // NOTA: O serverContent geralmente traz a fala da IA, não do usuário.
                        // Usamos o SpeechRecognition para o usuário.

                        const parts = message.serverContent?.modelTurn?.parts || [];

                        const fnCall = parts.find(p => p.functionCall)?.functionCall;
                        if (fnCall) handleFunctionCall(fnCall);

                        const audio = parts.find(p => p.inlineData)?.inlineData;
                        if (!audio) return;

                        const ctx = outputAudioContextRef.current;
                        if (ctx.state === 'suspended') await ctx.resume();

                        nextStartTimeRef.current = Math.max(nextStartTimeRef.current, ctx.currentTime);
                        try {
                            const audioBuffer = await decodeAudioData(decode(audio.data), ctx, 24000, 1);
                            const source = ctx.createBufferSource();
                            source.buffer = audioBuffer;
                            source.connect(outputNodeRef.current);
                            source.start(nextStartTimeRef.current);
                            nextStartTimeRef.current += audioBuffer.duration;
                            sourcesRef.current.add(source);
                        } catch (err) {
                            console.error("❌ EVA: Erro ao decodificar áudio de resposta:", err);
                        }
                    },
                    onclose: (e) => console.log('🔒 EVA: Sessão fechada pelo servidor', e),
                    onerror: (e) => console.error('❌ EVA: Erro na sessão:', e),
                },
            });
        } catch (err) {
            console.error("❌ EVA: Erro ao conectar sessão:", err);
            setIsConnecting(false);
        }
    };

    const startConversation = async () => {
        console.log("▶️ EVA: Iniciando conversa...");
        await initSession();

        try {
            await inputAudioContextRef.current.resume();
            await outputAudioContextRef.current.resume();

            console.log("🎤 EVA: Solicitando microfone...");
            mediaStreamRef.current = await navigator.mediaDevices.getUserMedia({ audio: true });
            const source = inputAudioContextRef.current.createMediaStreamSource(mediaStreamRef.current);

            console.log("⚙️ EVA: Criando AudioWorkletNode...");
            const workletNode = new AudioWorkletNode(inputAudioContextRef.current, 'audio-processor');

            workletNode.port.onmessage = (event) => {
                // Checagem de segurança dupla
                if (!activeRef.current) return;

                if (sessionRef.current) {
                    try {
                        sessionRef.current.sendRealtimeInput({
                            media: createBlob(event.data),
                        });
                    } catch (err) {
                        // Erro silencioso esperado se o socket fechar abruptamente
                        if (!err.message?.includes("CLOSING")) {
                            console.warn("⚠️ EVA: Erro ao enviar áudio (pode ser normal no encerramento):", err);
                        }
                    }
                }
            };

            source.connect(workletNode);
            workletNode.connect(inputAudioContextRef.current.destination);
            workletNodeRef.current = workletNode;

            // Inicia o reconhecimento de fala nativo para legendas
            if (recognitionRef.current) {
                try {
                    recognitionRef.current.start();
                    console.log("🗣️ Speech Recognition iniciado");
                } catch (e) {
                    console.warn("⚠️ Speech Recognition já estava ativo ou falhou:", e);
                }
            }

            activeRef.current = true;
            setIsActive(true);
            console.log("✅ EVA: Conversa ativa!");
        } catch (err) {
            console.error("❌ EVA: Falha ao iniciar hardware:", err);
        }
    };

    const stopConversation = () => {
        console.log("⏹️ EVA: Parando conversa...");
        activeRef.current = false; // Trava imediata
        setIsActive(false);

        if (mediaStreamRef.current) {
            mediaStreamRef.current.getTracks().forEach(t => t.stop());
            console.log("   Microfone liberado.");
        }

        if (workletNodeRef.current) {
            workletNodeRef.current.disconnect();
            workletNodeRef.current.port.postMessage("STOP");
            console.log("   AudioWorklet desconectado.");
        }

        // Para o reconhecimento de fala nativo
        if (recognitionRef.current) {
            try {
                recognitionRef.current.stop();
                console.log("   Speech Recognition parado.");
            } catch (e) { }
        }

        sourcesRef.current.forEach(s => { try { s.stop(); } catch (e) { } });
        sourcesRef.current.clear();

        if (sessionRef.current) {
            sessionRef.current = null;
            console.log("   Sessão anulada.");
        }
        console.log("✅ EVA: Conversa parada com sucesso.");
    };

    return (
        <div className="fixed bottom-8 right-8 z-[9999]">
            <button
                disabled={!isReady || isConnecting}
                onClick={isActive ? stopConversation : startConversation}
                className={`w-16 h-16 rounded-full flex items-center justify-center transition-all duration-300 shadow-lg ${isActive
                    ? 'animate-pulse bg-red-500 shadow-red-500/50'
                    : 'bg-gradient-to-br from-pink-500 to-purple-600 hover:scale-110 shadow-purple-500/50'
                    } ${(!isReady || isConnecting) ? 'opacity-50 grayscale' : 'cursor-pointer'}`}
            >
                {isActive ? <MicOff className="w-8 h-8 text-white" /> : <Mic className="w-8 h-8 text-white" />}
            </button>
        </div>
    );
};

export default VoiceAssistant;