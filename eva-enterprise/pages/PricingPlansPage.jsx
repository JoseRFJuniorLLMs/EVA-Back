import React from 'react';
import { Check, Info } from 'lucide-react';

export default function PricingPlansPage() {
    const plans = [
        {
            name: 'Livre',
            price: '0',
            description: 'Experimente a organização do cuidado.',
            features: [
                'Interface acessível e intuitiva',
                'Cadastro do perfil do idoso',
                'Histórico completo de chamadas',
                'Botão "Ligar Agora" manual para testes'
            ],
            current: true,
            buttonText: 'Seu plano atual',
            buttonClass: 'bg-gray-200 text-gray-700 cursor-default'
        },
        {
            name: 'Essencial',
            price: '7,99',
            description: 'Automação para o dia a dia da família.',
            features: [
                'Lembretes automáticos de remédios',
                'Confirmação de tomada da medicação',
                'Personalização de áudio (volume adaptado)',
                'Evita esquecimentos perigosos',
                'Alertas básicos de "Não Atendeu"'
            ],
            current: false,
            buttonText: 'Assinar Essencial',
            buttonClass: 'bg-pink-600 text-white hover:bg-pink-700'
        },
        {
            name: 'Família+',
            price: '23',
            description: 'Segurança total e tranquilidade 24/7.',
            features: [
                'Tudo do plano Essencial',
                'Detecção de emergências (dor, quedas)',
                'Alertas vermelhos imediatos',
                'Monitoramento em tempo real',
                'Redução total de estresse e sobrecarga',
                'Relatórios detalhados de adesão'
            ],
            current: false,
            buttonText: 'Assinar Família+',
            buttonClass: 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:opacity-90'
        },
        {
            name: 'Profissional',
            price: '229',
            description: 'Para lares de idosos e clínicas.',
            features: [
                'Múltiplos idosos ilimitados',
                'Integrações futuras (Sensores, Smartwatch)',
                'Lembretes de consultas médicas',
                'Dados seguros e privados (HIPAA ready)',
                'Suporte prioritário dedicado',
                'API de integração'
            ],
            current: false,
            buttonText: 'Falar com Vendas',
            buttonClass: 'bg-black text-white hover:bg-gray-800'
        }
    ];

    return (
        <div className="p-8 bg-pink-50">
            <div className="w-full">
                <div className="text-center mb-16">
                    <h2 className="text-4xl font-extrabold text-pink-700 sm:text-5xl">
                        Escolha o cuidado ideal
                    </h2>
                    <p className="mt-4 text-xl text-gray-500">
                        Tecnologia humanizada para cuidar de quem você ama.
                    </p>
                </div>

                <div className="grid grid-cols-1 gap-8 md:grid-cols-2 xl:grid-cols-4">
                    {plans.map((plan) => (
                        <div
                            key={plan.name}
                            className={`bg-white rounded-2xl shadow-xl overflow-hidden border transition-transform hover:scale-105 ${plan.name === 'Família+' ? 'border-purple-200 ring-2 ring-purple-400' : 'border-pink-100'}`}
                        >
                            <div className="p-8">
                                <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                                <div className="flex items-baseline mb-4">
                                    <span className="text-4xl font-extrabold text-gray-900">R${plan.price}</span>
                                    <span className="text-gray-500 ml-2">/mês</span>
                                </div>
                                <p className="text-gray-500 text-sm mb-6 h-10">{plan.description}</p>

                                <button
                                    className={`w-full py-3 px-6 rounded-xl font-bold text-lg shadow-sm transition-colors mb-6 ${plan.buttonClass}`}
                                >
                                    {plan.buttonText}
                                </button>

                                <ul className="space-y-4">
                                    {plan.features.map((feature, index) => (
                                        <li key={index} className="flex items-start">
                                            <Check className="flex-shrink-0 w-5 h-5 text-green-500 mt-1" />
                                            <span className="ml-3 text-sm text-gray-600 leading-snug">{feature}</span>
                                        </li>
                                    ))}
                                </ul>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="mt-12 text-center text-gray-500 text-sm">
                    <p>Dúvidas sobre qual plano escolher? <button className="text-pink-600 hover:underline">Fale com nossa equipe</button></p>
                </div>
            </div>
        </div>
    );
}
