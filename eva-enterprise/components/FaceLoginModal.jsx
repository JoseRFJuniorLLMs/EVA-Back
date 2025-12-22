import React, { useRef, useState, useCallback } from 'react';
import Webcam from 'react-webcam';
import { ScanFace, X, CheckCircle, AlertCircle } from 'lucide-react';

const FaceLoginModal = ({ isOpen, onClose, onLoginSuccess }) => {
    const webcamRef = useRef(null);
    const [isScanning, setIsScanning] = useState(false);
    const [status, setStatus] = useState('idle'); // idle, scanning, success, error

    const capture = useCallback(() => {
        setIsScanning(true);
        setStatus('scanning');

        // Simulação de processamento (2 segundos)
        setTimeout(() => {
            const imageSrc = webcamRef.current.getScreenshot();
            console.log("📸 Imagem capturada para verificação:", imageSrc);

            // EM UM CENÁRIO REAL: Enviar imageSrc para backend comparar com 'eu.png'
            // AQUI: Simular sucesso se houver imagem
            if (imageSrc) {
                setStatus('success');
                setTimeout(() => {
                    onLoginSuccess();
                }, 1000);
            } else {
                setStatus('error');
                setIsScanning(false);
            }
        }, 2000);
    }, [webcamRef, onLoginSuccess]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 bg-black/90 flex items-center justify-center z-50 p-4">
            <div className="bg-gray-900 border border-gray-700 rounded-2xl p-6 w-full max-w-md relative shadow-2xl">
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
                >
                    <X className="w-6 h-6" />
                </button>

                <div className="text-center mb-6">
                    <h2 className="text-2xl font-bold text-white mb-2 flex items-center justify-center gap-2">
                        <ScanFace className="w-8 h-8 text-pink-500" />
                        Face ID
                    </h2>
                    <p className="text-gray-400 text-sm">Olhe para a câmera para autenticar</p>
                </div>

                <div className="relative rounded-xl overflow-hidden aspect-video bg-black mb-6 border-2 border-dashed border-gray-600">
                    <Webcam
                        audio={false}
                        ref={webcamRef}
                        screenshotFormat="image/jpeg"
                        className="w-full h-full object-cover"
                        videoConstraints={{ facingMode: "user" }}
                    />

                    {/* Overlay de Scanning */}
                    {status === 'scanning' && (
                        <div className="absolute inset-0 bg-pink-500/10 flex items-center justify-center">
                            <div className="w-full h-1 bg-pink-500 shadow-[0_0_20px_#ec4899] animate-[scan_2s_ease-in-out_infinite]" />
                        </div>
                    )}

                    {/* Overlay de Sucesso */}
                    {status === 'success' && (
                        <div className="absolute inset-0 bg-green-500/20 backdrop-blur-sm flex items-center justify-center flex-col animate-in fade-in duration-300">
                            <CheckCircle className="w-16 h-16 text-green-400 mb-2" />
                            <span className="text-green-400 font-bold text-lg">Identidade Confirmada</span>
                        </div>
                    )}
                </div>

                <div className="flex justify-center">
                    {status === 'idle' || status === 'error' ? (
                        <button
                            onClick={capture}
                            className="bg-pink-600 hover:bg-pink-700 text-white px-8 py-3 rounded-full font-bold shadow-lg shadow-pink-900/50 transition-all active:scale-95 flex items-center gap-2"
                        >
                            <ScanFace className="w-5 h-5" />
                            Escanear Rosto
                        </button>
                    ) : (
                        <div className="text-pink-400 font-medium animate-pulse">
                            Processando biometria...
                        </div>
                    )}
                </div>
            </div>

            <style>{`
                @keyframes scan {
                    0% { transform: translateY(-100px); opacity: 0; }
                    50% { opacity: 1; }
                    100% { transform: translateY(100px); opacity: 0; }
                }
            `}</style>
        </div>
    );
};

export default FaceLoginModal;
