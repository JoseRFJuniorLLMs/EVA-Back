import React, { useState } from 'react';
import { createUserWithEmailAndPassword, updateProfile } from 'firebase/auth'; // Added updateProfile
import { doc, setDoc } from 'firebase/firestore'; // Added Firestore functions
import { auth, db } from '../services/firebase'; // Added db
import { useNavigate, Link } from 'react-router-dom';

const RegisterPage = () => {
    // Componente de Cadastro conectado ao Firebase
    const [name, setName] = useState(''); // Estado para Nome
    const [cpf, setCpf] = useState('');   // Estado para CPF
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleRegister = async (e) => {
        e.preventDefault();

        if (password !== confirmPassword) {
            setError('As senhas não coincidem.');
            return;
        }

        if (password.length < 6) {
            setError('A senha deve ter pelo menos 6 caracteres.');
            return;
        }

        if (cpf.length < 11) {
            setError('Por favor, insira um CPF válido.');
            return;
        }

        try {
            setError('');
            // 1. Criar usuário na Autenticação
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            const user = userCredential.user;

            // 2. Atualizar o nome de exibição no perfil do Auth
            await updateProfile(user, {
                displayName: name
            });

            // 3. Salvar dados extras (CPF, Nome) no Firestore
            await setDoc(doc(db, "users", user.uid), {
                uid: user.uid,
                nome: name,
                email: email,
                cpf: cpf.replace(/\D/g, ''), // Salva apenas números
                createdAt: new Date().toISOString(),
                role: 'responsavel' // Define o papel como responsável
            });

            navigate('/planos'); // Redireciona para escolher o plano após cadastro
        } catch (err) {
            console.error("Erro completo do Firebase:", err);
            console.log("Código do erro:", err.code);

            let mensagem = 'Erro ao criar conta.';
            if (err.code === 'auth/email-already-in-use') {
                mensagem = 'Este e-mail já está em uso.';
            } else if (err.code === 'auth/invalid-email') {
                mensagem = 'Formato de e-mail inválido.';
            } else if (err.code === 'auth/weak-password') {
                mensagem = 'A senha é muito fraca.';
            } else if (err.code === 'auth/configuration-not-found') {
                mensagem = 'Erro de configuração: O login por E-mail/Senha não está ativado no Firebase Console.';
            } else if (err.code === 'auth/operation-not-allowed') {
                mensagem = 'Erro: Criação de contas por e-mail/senha não está habilitada.';
            }

            setError(mensagem);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-pink-50">
            <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md border border-pink-100">
                <h2 className="text-3xl font-bold text-center text-pink-600 mb-8">Criar Conta EVA</h2>
                {error && <div className="bg-red-100 text-red-700 p-3 rounded-lg mb-4 text-sm">{error}</div>}
                <form onSubmit={handleRegister} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Nome do Responsável</label>
                        <input
                            type="text"
                            required
                            placeholder="Seu nome completo"
                            className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-pink-500 focus:ring-2 focus:ring-pink-200 outline-none transition-all"
                            value={name}
                            onChange={(e) => setName(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">CPF</label>
                        <input
                            type="text"
                            required
                            placeholder="Apenas números"
                            className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-pink-500 focus:ring-2 focus:ring-pink-200 outline-none transition-all"
                            value={cpf}
                            onChange={(e) => setCpf(e.target.value)}
                            maxLength={14}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                        <input
                            type="email"
                            required
                            className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-pink-500 focus:ring-2 focus:ring-pink-200 outline-none transition-all"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Senha</label>
                        <input
                            type="password"
                            required
                            className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-pink-500 focus:ring-2 focus:ring-pink-200 outline-none transition-all"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">Confirmar Senha</label>
                        <input
                            type="password"
                            required
                            className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:border-pink-500 focus:ring-2 focus:ring-pink-200 outline-none transition-all"
                            value={confirmPassword}
                            onChange={(e) => setConfirmPassword(e.target.value)}
                        />
                    </div>
                    <button
                        type="submit"
                        className="w-full py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-xl font-bold shadow-md hover:shadow-lg transform active:scale-95 transition-all"
                    >
                        Cadastrar
                    </button>
                </form>
                <div className="mt-6 text-center">
                    <p className="text-gray-600">
                        Já tem uma conta?{' '}
                        <Link to="/login" className="text-pink-600 font-bold hover:underline">
                            Fazer Login
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default RegisterPage;
