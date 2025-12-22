import React, { useState } from 'react';
import { CreditCard, Plus, Search, DollarSign, CheckCircle, Clock, QrCode, Shield } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';

export default function PagamentosPage() {
    const { pagamentos, formasPagamento } = useEva();
    const [searchTerm, setSearchTerm] = useState('');

    const filteredPagamentos = pagamentos.filter(p =>
        p.descricao.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.metodo.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.status.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <div className="p-8">
            <h2 className="text-3xl font-bold text-pink-700 mb-8 flex items-center gap-3">
                <DollarSign className="w-8 h-8" />
                Gestão Financeira
            </h2>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-10">
                {/* Métodos de Pagamento */}
                <div className="lg:col-span-1 bg-white rounded-3xl shadow-xl p-8 border border-pink-50 flex flex-col">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-xl font-black text-gray-900 leading-tight">Formas de Pagamento</h3>
                        <button className="p-2 bg-pink-100 text-pink-600 rounded-xl hover:bg-pink-200 transition-colors">
                            <Plus className="w-6 h-6" />
                        </button>
                    </div>

                    <div className="space-y-4 flex-1">
                        {formasPagamento.map(forma => (
                            <div key={forma.id} className={`p-5 rounded-2xl border-2 transition-all flex items-center justify-between ${forma.principal ? 'border-pink-500 bg-pink-50/30' : 'border-gray-100 bg-gray-50'}`}>
                                <div className="flex items-center gap-4">
                                    <div className={`p-3 rounded-xl ${forma.tipo === 'cartao' ? 'bg-blue-100 text-blue-600' : 'bg-green-100 text-green-600'}`}>
                                        {forma.tipo === 'cartao' ? <CreditCard className="w-6 h-6" /> : <QrCode className="w-6 h-6" />}
                                    </div>
                                    <div>
                                        <p className="font-bold text-gray-900">{forma.detalhe}</p>
                                        {forma.principal && <span className="text-[10px] font-black uppercase text-pink-600 tracking-widest">Principal</span>}
                                    </div>
                                </div>
                                <button className="text-xs font-bold text-gray-400 hover:text-pink-600 transition-colors">Remover</button>
                            </div>
                        ))}
                    </div>

                    <div className="mt-8 p-4 bg-indigo-50 rounded-2xl border border-indigo-100 flex items-start gap-3">
                        <Shield className="w-5 h-5 text-indigo-600 shrink-0" />
                        <p className="text-[10px] text-indigo-800 font-bold leading-relaxed uppercase tracking-widest">
                            Seus dados estão protegidos por criptografia de ponta a ponta padrão Enterprise.
                        </p>
                    </div>
                </div>

                {/* Lista de Pagamentos */}
                <div className="lg:col-span-2 bg-white rounded-3xl shadow-xl border border-pink-50 overflow-hidden flex flex-col">
                    <div className="p-8 border-b flex flex-col md:flex-row justify-between items-center gap-4">
                        <h3 className="text-xl font-black text-gray-900 leading-tight shrink-0">Histórico de Cobrança</h3>
                        <div className="flex-1 w-full relative">
                            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Buscar pagamentos..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="w-full pl-12 pr-4 py-3 bg-gray-50 border border-gray-100 rounded-2xl focus:outline-none focus:border-pink-400 transition-colors font-medium"
                            />
                        </div>
                    </div>

                    <div className="flex-1 overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead className="bg-gray-50 text-pink-700 uppercase text-[10px] font-black tracking-widest border-b">
                                <tr>
                                    <th className="px-8 py-5">Data</th>
                                    <th className="px-8 py-5">Descrição</th>
                                    <th className="px-8 py-5">Valor</th>
                                    <th className="px-8 py-5">Método</th>
                                    <th className="px-8 py-5">Status</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-50">
                                {filteredPagamentos.map(pag => (
                                    <tr key={pag.id} className="hover:bg-pink-50/20 transition-colors">
                                        <td className="px-8 py-5 text-sm font-bold text-gray-400 font-mono">{pag.data}</td>
                                        <td className="px-8 py-5 text-sm font-bold text-gray-900">{pag.descricao}</td>
                                        <td className="px-8 py-5 text-sm font-black text-pink-600">R$ {pag.valor.toLocaleString('pt-BR', { minimumFractionDigits: 2 })}</td>
                                        <td className="px-8 py-5 text-sm font-medium text-gray-500">{pag.metodo}</td>
                                        <td className="px-8 py-5">
                                            <span className={`flex items-center gap-1.5 px-3 py-1 rounded-lg text-[10px] font-black uppercase tracking-wider w-fit ${pag.status === 'pago' ? 'bg-green-100 text-green-700' : 'bg-amber-100 text-amber-700'
                                                }`}>
                                                {pag.status === 'pago' ? <CheckCircle className="w-3 h-3" /> : <Clock className="w-3 h-3" />}
                                                {pag.status === 'pago' ? 'Pago' : 'Pendente'}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
}
