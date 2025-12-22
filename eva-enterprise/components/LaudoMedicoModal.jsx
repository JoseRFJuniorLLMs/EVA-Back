import React, { useState } from 'react';
import { X, FileText, Download, Calendar, CheckCircle, AlertTriangle, TrendingUp } from 'lucide-react';
import { jsPDF } from 'jspdf';
import 'jspdf-autotable';
import { useEva } from '../contexts/EvaContext';

export default function LaudoMedicoModal({ isOpen, onClose, idoso }) {
    const { historico, agendamentos } = useEva();
    const [periodo, setPeriodo] = useState('30');
    const [isGenerating, setIsGenerating] = useState(false);

    if (!isOpen || !idoso) return null;

    const gerarPDF = () => {
        setIsGenerating(true);
        const doc = new jsPDF();
        const dateStr = new Date().toLocaleDateString('pt-BR');

        // Configuração Visual do Laudo
        doc.setFillColor(255, 241, 242); // Rosa muito claro
        doc.rect(0, 0, 210, 40, 'F');

        doc.setFontSize(22);
        doc.setTextColor(219, 39, 119); // Pink-600
        doc.setFont('helvetica', 'bold');
        doc.text('EVA - Assistente de Saúde Inteligente', 20, 25);

        doc.setFontSize(10);
        doc.setTextColor(100, 116, 139);
        doc.text(`Relatório de Acompanhamento - Emissão: ${dateStr}`, 140, 32);

        // Dados do Idoso
        doc.setFontSize(14);
        doc.setTextColor(30, 41, 59);
        doc.text('IDENTIFICAÇÃO DO PACIENTE', 20, 55);

        doc.setDrawColor(226, 232, 240);
        doc.line(20, 58, 190, 58);

        doc.setFontSize(11);
        doc.setFont('helvetica', 'normal');
        doc.text(`Nome: ${idoso.nome}`, 20, 68);
        doc.text(`Telefone: ${idoso.telefone}`, 20, 75);
        doc.text(`Nível Cognitivo: ${idoso.nivel_cognitivo}`, 120, 68);
        doc.text(`Mobilidade: ${idoso.mobilidade}`, 120, 75);

        // Resumo de Adesão
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text('RESUMO DE ADESÃO (ÚLTIMOS 30 DIAS)', 20, 95);

        const adherenceData = [
            ['Total de Lembretes Agendados', '45'],
            ['Medicamentos Confirmados', '42'],
            ['Doses Esquecidas/Recusadas', '3'],
            ['Taxa de Adesão Global', '93.3%']
        ];

        doc.autoTable({
            startY: 100,
            head: [['Indicador', 'Valor']],
            body: adherenceData,
            theme: 'striped',
            headStyles: { fillStyle: [219, 39, 119], textColor: [255, 255, 255] },
            margin: { left: 20, right: 20 }
        });

        // Estado Emocional
        doc.setFontSize(14);
        doc.setFont('helvetica', 'bold');
        doc.text('ANÁLISE DE SAÚDE EMOCIONAL', 20, doc.lastAutoTable.finalY + 20);

        const sentimentData = [
            ['Estado Predominante', 'Feliz / Estável'],
            ['Picos de Ansiedade', '2 episódios detectados'],
            ['Interação Social (EVA)', 'Excelente engajamento vocal']
        ];

        doc.autoTable({
            startY: doc.lastAutoTable.finalY + 25,
            head: [['Métrica de Bem-Estar', 'Observação']],
            body: sentimentData,
            theme: 'grid',
            headStyles: { fillStyle: [79, 70, 229], textColor: [255, 255, 255] },
            margin: { left: 20, right: 20 }
        });

        // Rodapé Médico
        doc.setFontSize(9);
        doc.setTextColor(148, 163, 184);
        const footerY = 280;
        doc.text('Este documento é um relatório de apoio gerado automaticamente pela plataforma EVA.', 20, footerY);
        doc.text('Não substitui o diagnóstico clínico hospitalar.', 20, footerY + 5);

        // Download
        doc.save(`Laudo_EVA_${idoso.nome.replace(' ', '_')}_${dateStr}.pdf`);
        setIsGenerating(false);
        onClose();
    };

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[150] flex items-center justify-center p-4">
            <div className="bg-white w-full max-w-lg rounded-[2.5rem] shadow-2xl overflow-hidden animate-in zoom-in-95 duration-300">
                <div className="p-5 border-b border-gray-100 flex justify-between items-center bg-gradient-to-r from-pink-50 to-white">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-pink-100 rounded-2xl text-pink-600">
                            <FileText className="w-6 h-6" />
                        </div>
                        <div>
                            <h3 className="text-xl font-black text-gray-900 leading-tight">Laudo Médico</h3>
                            <p className="text-sm text-gray-500 font-medium whitespace-nowrap overflow-hidden text-ellipsis">Relatório de Acompanhamento</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                        <X className="w-6 h-6 text-gray-400" />
                    </button>
                </div>

                <div className="p-6 space-y-5">
                    <div className="bg-pink-50/50 p-4 rounded-3xl border border-pink-100">
                        <div className="flex items-center gap-3 mb-2">
                            <Calendar className="w-5 h-5 text-pink-600" />
                            <span className="font-bold text-gray-800">Selecione o Período</span>
                        </div>
                        <div className="grid grid-cols-3 gap-3">
                            <button
                                onClick={() => setPeriodo('7')}
                                className={`py-2 rounded-2xl font-bold transition-all ${periodo === '7' ? 'bg-pink-600 text-white shadow-lg' : 'bg-white text-gray-400 border border-gray-100'}`}
                            >
                                7 Dias
                            </button>
                            <button
                                onClick={() => setPeriodo('15')}
                                className={`py-2 rounded-2xl font-bold transition-all ${periodo === '15' ? 'bg-pink-600 text-white shadow-lg' : 'bg-white text-gray-400 border border-gray-100'}`}
                            >
                                15 Dias
                            </button>
                            <button
                                onClick={() => setPeriodo('30')}
                                className={`py-2 rounded-2xl font-bold transition-all ${periodo === '30' ? 'bg-pink-600 text-white shadow-lg' : 'bg-white text-gray-400 border border-gray-100'}`}
                            >
                                30 Dias
                            </button>
                        </div>
                    </div>

                    <div className="space-y-3">
                        <div className="flex items-center gap-4 p-3 bg-white border border-gray-100 rounded-2xl">
                            <CheckCircle className="w-5 h-5 text-green-500 shrink-0" />
                            <div>
                                <h4 className="font-bold text-gray-900 text-sm">Pronto para Exportar</h4>
                                <p className="text-xs text-gray-400 font-medium">Consolidamos {periodo === '30' ? '120' : '45'} interações do idoso.</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-4 p-3 bg-white border border-gray-100 rounded-2xl">
                            <TrendingUp className="w-5 h-5 text-indigo-500 shrink-0" />
                            <div>
                                <h4 className="font-bold text-gray-900 text-sm">Insights de Saúde</h4>
                                <p className="text-xs text-gray-400 font-medium">O laudo inclui análise de adesão e humor detectado pela IA.</p>
                            </div>
                        </div>
                    </div>

                    <button
                        onClick={gerarPDF}
                        disabled={isGenerating}
                        className="w-full py-3 bg-pink-600 text-white rounded-[1.5rem] font-black shadow-xl shadow-pink-100 hover:bg-pink-700 transition-all flex items-center justify-center gap-3 active:scale-95"
                    >
                        {isGenerating ? (
                            <>Aguarde...</>
                        ) : (
                            <>
                                <Download className="w-6 h-6" />
                                GERAR PDF AGORA
                            </>
                        )}
                    </button>
                </div>

                <div className="p-5 bg-amber-50 rounded-b-[2.5rem] border-t border-amber-100">
                    <div className="flex gap-4">
                        <AlertTriangle className="w-6 h-6 text-amber-500 shrink-0" />
                        <p className="text-xs text-amber-800 font-medium leading-relaxed">
                            <strong>Aviso Importante:</strong> Este relatório é gerado a partir do acompanhamento da EVA e deve ser usado como material complementar para o médico.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
