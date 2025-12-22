import React from 'react';
import { useAuth } from '../hooks/useAuth';
import { LogOut } from 'lucide-react';
import { signOut } from 'firebase/auth';
import { auth } from '../services/firebase';
import { useTranslation } from 'react-i18next';
import LanguageSelector from './LanguageSelector';

export default function Header() {
    const { user } = useAuth();
    const { t } = useTranslation();

    const handleLogout = () => signOut(auth);

    return (
        <header className="bg-gradient-to-r from-pink-500 to-purple-600 text-white shadow-lg h-20">
            <div className="px-8 h-full flex justify-between items-center">
                <div className="flex flex-col">
                    <h1 className="text-2xl font-bold">{t('appTitle')}</h1>
                    <span className="text-xs opacity-80">{t('portalSubtitle')}</span>
                </div>

                <div className="flex items-center gap-6">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                        <span className="font-medium text-sm">Online</span>
                    </div>

                    <div className="flex items-center gap-3">
                        <div className="text-right hidden md:block">
                            <p className="text-sm font-bold">{user?.displayName || t('responsavel')}</p>
                            <p className="text-xs opacity-80">{user?.email}</p>
                        </div>
                        <button onClick={handleLogout} className="p-2 hover:bg-white/10 rounded-full transition-colors" title="Sair">
                            <LogOut className="w-5 h-5" />
                        </button>
                        <LanguageSelector />
                    </div>
                </div>
            </div>
        </header>
    );
}
