import React, { useState } from 'react';
import { signInWithEmailAndPassword } from 'firebase/auth';
import { auth } from '../services/firebase';
import { useNavigate, Link } from 'react-router-dom';
import FaceLoginModal from '../components/FaceLoginModal';
import { ScanFace } from 'lucide-react';

const LoginPage = () => {
    // Componente de Login conectado ao Firebase
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isFaceLoginOpen, setIsFaceLoginOpen] = useState(false);
    const navigate = useNavigate();

    const handleLogin = async (e) => {
        e.preventDefault();
        try {
            setError('');
            await signInWithEmailAndPassword(auth, email, password);
            navigate('/');
        } catch (err) {
            console.error("Erro completo do Firebase:", err);
            console.log("Código do erro:", err.code);

            let mensagem = 'Erro ao fazer login.';
            if (err.code === 'auth/invalid-credential' || err.code === 'auth/user-not-found' || err.code === 'auth/wrong-password') {
                mensagem = 'E-mail ou senha incorretos.';
            } else if (err.code === 'auth/invalid-email') {
                mensagem = 'Formato de e-mail inválido.';
            } else if (err.code === 'auth/too-many-requests') {
                mensagem = 'Muitas tentativas falhas. Tente novamente mais tarde.';
            }

            setError(mensagem);
        }
    }

    const handleFaceLoginSuccess = () => {
        setIsFaceLoginOpen(false);
        navigate('/'); // Simula login bem-sucedido via Face ID
    };


    return (
        <div className="min-h-screen flex items-center justify-center bg-pink-50">
            <div className="bg-white p-8 rounded-2xl shadow-xl w-full max-w-md border border-pink-100">
                <h2 className="text-3xl font-bold text-center text-pink-600 mb-8">EVA Portal da Familia</h2>
                {error && <div className="bg-red-100 text-red-700 p-3 rounded-lg mb-4 text-sm">{error}</div>}
                <form onSubmit={handleLogin} className="space-y-6">
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

                    <div className="flex flex-col gap-3 pt-2">
                        <button
                            type="submit"
                            className="w-full py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-xl font-bold shadow-md hover:shadow-lg transform active:scale-95 transition-all"
                        >
                            Entrar
                        </button>

                        <div className="relative flex py-2 items-center">
                            <div className="flex-grow border-t border-gray-200"></div>
                            <span className="flex-shrink-0 mx-4 text-gray-400 text-sm">ou</span>
                            <div className="flex-grow border-t border-gray-200"></div>
                        </div>

                        <button
                            type="button"
                            onClick={() => setIsFaceLoginOpen(true)}
                            className="w-full py-3 bg-white text-gray-700 border-2 border-gray-200 rounded-xl font-bold hover:bg-gray-50 hover:border-pink-300 hover:text-pink-600 transition-all flex items-center justify-center gap-2"
                        >
                            <ScanFace className="w-5 h-5" />
                            Entrar com Face ID
                        </button>
                    </div>
                </form>
                <div className="mt-6 text-center">
                    <p className="text-gray-600">
                        Não tem uma conta?{' '}
                        <Link to="/register" className="text-pink-600 font-bold hover:underline">
                            Criar Conta
                        </Link>
                    </p>
                </div>
            </div>

            <FaceLoginModal
                isOpen={isFaceLoginOpen}
                onClose={() => setIsFaceLoginOpen(false)}
                onLoginSuccess={handleFaceLoginSuccess}
            />
        </div>
    );
};

export default LoginPage;
