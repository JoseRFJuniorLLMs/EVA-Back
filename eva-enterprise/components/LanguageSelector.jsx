import React from 'react';
import { useTranslation } from 'react-i18next';
import 'flag-icons/css/flag-icons.min.css';

const languages = [
    { code: 'pt', label: 'Português', flagClass: 'fi-br' },
    { code: 'en', label: 'English', flagClass: 'fi-us' },
    { code: 'es', label: 'Español', flagClass: 'fi-es' },
];

export default function LanguageSelector() {
    const { i18n, t } = useTranslation();

    const changeLanguage = (lng) => {
        i18n.changeLanguage(lng);
    };

    return (
        <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-white">{t('language')}:</span>
            {languages.map((l) => (
                <button
                    key={l.code}
                    onClick={() => changeLanguage(l.code)}
                    className={`p-1 rounded ${i18n.language === l.code ? 'bg-white/20' : ''}`}
                    title={l.label}
                >
                    <span className={`fi ${l.flagClass} w-5 h-5 rounded-sm`}></span>
                </button>
            ))}
        </div>
    );
}
