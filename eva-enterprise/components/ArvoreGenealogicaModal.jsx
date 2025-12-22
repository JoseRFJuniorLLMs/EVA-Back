import React from 'react';
import { X, Network, User, Heart, Star } from 'lucide-react';
import { useEva } from '../contexts/EvaContext';

export default function ArvoreGenealogicaModal({ isOpen, onClose, idoso }) {
    const { genealogia } = useEva();

    if (!isOpen || !idoso) return null;

    const membros = genealogia.filter(m => m.idoso_id === idoso.id);

    // Organiza por níveis
    const treeData = {
        elder: membros.find(m => m.level === 0),
        children: membros.filter(m => m.level === 1),
        grandchildren: membros.filter(m => m.level === 2)
    };

    const MemberCard = ({ member, size = "large" }) => (
        <div className={`relative flex flex-col items-center group ${size === "large" ? "scale-110 mb-8" : ""}`}>
            <div className={`
                relative rounded-full p-1 border-4 transition-all
                ${member.parentesco.includes('Responsável') ? 'border-pink-500 shadow-pink-100' : 'border-gray-100 shadow-gray-50'}
                group-hover:scale-105 shadow-xl bg-white
            `}>
                <img
                    src={member.foto}
                    alt={member.nome}
                    className={`${size === "large" ? "w-24 h-24" : "w-16 h-16"} rounded-full object-cover`}
                />
                {member.parentesco.includes('Responsável') && (
                    <div className="absolute -top-2 -right-2 bg-pink-600 text-white p-1 rounded-full shadow-lg">
                        <Star className="w-3 h-3 fill-current" />
                    </div>
                )}
            </div>
            <div className="mt-3 text-center bg-white/80 backdrop-blur-md px-4 py-2 rounded-2xl shadow-sm border border-gray-50">
                <p className="font-black text-gray-900 text-sm">{member.nome}</p>
                <p className="text-[10px] font-bold text-pink-500 uppercase tracking-tighter">{member.parentesco}</p>
            </div>
        </div>
    );

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-[150] flex items-center justify-center p-4">
            <div className="bg-gray-50 w-full max-w-5xl h-[85vh] rounded-[3rem] shadow-2xl overflow-hidden flex flex-col animate-in zoom-in-95 duration-300 border-8 border-white">

                {/* Header */}
                <div className="p-8 border-b border-gray-100 flex justify-between items-center bg-white">
                    <div className="flex items-center gap-4">
                        <div className="p-3 bg-indigo-100 rounded-2xl text-indigo-600">
                            <Network className="w-8 h-8" />
                        </div>
                        <div>
                            <h3 className="text-2xl font-black text-gray-900 leading-tight">Árvore Genealógica</h3>
                            <p className="text-gray-500 font-medium">Linhagem Familiar de {idoso.nome}</p>
                        </div>
                    </div>
                    <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-full transition-colors">
                        <X className="w-8 h-8 text-gray-400" />
                    </button>
                </div>

                {/* Tree Canvas */}
                <div className="flex-1 overflow-auto p-12 bg-[radial-gradient(#e5e7eb_1px,transparent_1px)] [background-size:24px_24px]">
                    <div className="min-w-max flex flex-col items-center gap-16 pb-20">

                        {/* Level 0: Elder */}
                        {treeData.elder && (
                            <div className="relative">
                                <MemberCard member={treeData.elder} />
                                {/* Conector para filhos */}
                                {treeData.children.length > 0 && (
                                    <div className="absolute top-full left-1/2 w-0.5 h-16 bg-pink-200 -ml-px"></div>
                                )}
                            </div>
                        )}

                        {/* Level 1: Children */}
                        <div className="relative flex gap-16">
                            {/* Linha horizontal conectora entre filhos */}
                            {treeData.children.length > 1 && (
                                <div className="absolute top-0 left-[20%] right-[20%] h-0.5 bg-pink-100"></div>
                            )}

                            {treeData.children.map(child => (
                                <div key={child.id} className="relative flex flex-col items-center">
                                    {/* Conector vertical subindo para o pai */}
                                    <div className="absolute -top-4 w-0.5 h-4 bg-pink-100"></div>

                                    <MemberCard member={child} size="medium" />

                                    {/* Conector para netos */}
                                    {treeData.grandchildren.some(g => g.parent_id === child.id) && (
                                        <div className="absolute top-full left-1/2 w-0.5 h-12 bg-indigo-100 -ml-px"></div>
                                    )}

                                    {/* Level 2: Grandchildren */}
                                    <div className="mt-12 flex gap-8">
                                        {treeData.grandchildren
                                            .filter(g => g.parent_id === child.id)
                                            .map(grandchild => (
                                                <div key={grandchild.id} className="relative flex flex-col items-center">
                                                    <div className="absolute -top-4 w-0.5 h-4 bg-indigo-50"></div>
                                                    <MemberCard member={grandchild} size="small" />
                                                </div>
                                            ))
                                        }
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                <div className="p-8 bg-white border-t border-gray-100">
                    <div className="flex justify-between items-center text-xs">
                        <div className="flex gap-6">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-pink-500"></div>
                                <span className="font-bold text-gray-500 uppercase tracking-widest">Responsável</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-indigo-400"></div>
                                <span className="font-bold text-gray-500 uppercase tracking-widest">Membros Vivos</span>
                            </div>
                        </div>
                        <p className="font-medium text-gray-400 italic">Visualize a rede de carinho que envolve o idoso.</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
