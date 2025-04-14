import { Bell, Database, Globe, Save, Sliders } from 'lucide-react'
import { useState } from 'react'

export function SettingsPage() {
    const [activeTab, setActiveTab] = useState('appearance')

    return (
        <div className="px-4 sm:px-6 lg:px-8 py-8">
            <div className="mb-8">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Configurações</h1>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Gerencie as preferências do sistema</p>
            </div>

            <div className="flex flex-col md:flex-row gap-8">
                {/* Settings Navigation */}
                <div className="w-full md:w-64 shrink-0">
                    <nav className="space-y-1">
                        {[
                            { id: 'appearance', name: 'Aparência', icon: Globe },
                            { id: 'notifications', name: 'Notificações', icon: Bell },
                            { id: 'data', name: 'Dados', icon: Database },
                            { id: 'advanced', name: 'Avançado', icon: Sliders }
                        ].map((item) => (
                            <button
                                key={item.id}
                                onClick={() => setActiveTab(item.id)}
                                className={`flex items-center px-3 py-2 text-sm font-medium rounded-md w-full ${activeTab === item.id
                                    ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'
                                    : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700/30'
                                    }`}
                            >
                                <item.icon className={`mr-3 h-5 w-5 ${activeTab === item.id
                                    ? 'text-blue-500 dark:text-blue-400'
                                    : 'text-gray-400 dark:text-gray-500'
                                    }`} />
                                {item.name}
                            </button>
                        ))}
                    </nav>
                </div>

                {/* Settings Content */}
                <div className="flex-1">
                    <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
                        {/* Appearance Tab */}
                        {activeTab === 'appearance' && (
                <div className="p-6">
                                <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-5">Configurações de Aparência</h2>

                    <div className="space-y-6">
                        <div>
                                        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Tema</h3>
                                        <div className="mt-2 space-y-3">
                                            <div className="flex items-center">
                                                <input
                                                    id="light"
                                                    name="theme"
                                                    type="radio"
                                                    defaultChecked
                                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                                                />
                                                <label htmlFor="light" className="ml-3 block text-sm font-medium text-gray-700 dark:text-gray-300">
                                                    Claro
                                                </label>
                                            </div>
                                            <div className="flex items-center">
                                                <input
                                                    id="dark"
                                                    name="theme"
                                                    type="radio"
                                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                                                />
                                                <label htmlFor="dark" className="ml-3 block text-sm font-medium text-gray-700 dark:text-gray-300">
                                                    Escuro
                                                </label>
                                            </div>
                                            <div className="flex items-center">
                                                <input
                                                    id="system"
                                                    name="theme"
                                                    type="radio"
                                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                                                />
                                                <label htmlFor="system" className="ml-3 block text-sm font-medium text-gray-700 dark:text-gray-300">
                                                    Sistema (usar preferência do sistema)
                            </label>
                                            </div>
                                        </div>
                        </div>

                        <div>
                                        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Densidade</h3>
                                        <div className="mt-2 space-y-3">
                                            <div className="flex items-center">
                                                <input
                                                    id="compact"
                                                    name="density"
                                                    type="radio"
                                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                                                />
                                                <label htmlFor="compact" className="ml-3 block text-sm font-medium text-gray-700 dark:text-gray-300">
                                                    Compacta
                                                </label>
                                            </div>
                                            <div className="flex items-center">
                                                <input
                                                    id="default"
                                                    name="density"
                                                    type="radio"
                                                    defaultChecked
                                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                                                />
                                                <label htmlFor="default" className="ml-3 block text-sm font-medium text-gray-700 dark:text-gray-300">
                                                    Padrão
                                                </label>
                                            </div>
                                            <div className="flex items-center">
                                                <input
                                                    id="comfortable"
                                                    name="density"
                                                    type="radio"
                                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                                                />
                                                <label htmlFor="comfortable" className="ml-3 block text-sm font-medium text-gray-700 dark:text-gray-300">
                                                    Confortável
                            </label>
                                            </div>
                                        </div>
                        </div>

                        <div>
                                        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Animações</h3>
                                <div className="flex items-center">
                                    <input
                                                id="animations"
                                        type="checkbox"
                                                defaultChecked
                                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                    />
                                            <label htmlFor="animations" className="ml-2 block text-sm text-gray-700 dark:text-gray-300">
                                                Habilitar animações de interface
                                    </label>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Notifications Tab */}
                        {activeTab === 'notifications' && (
                            <div className="p-6">
                                <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-5">Configurações de Notificações</h2>

                                <div className="space-y-6">
                                    <div>
                                        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Notificações do sistema</h3>
                                        <div className="space-y-3">
                                            <div className="flex items-center justify-between">
                                                <div className="flex flex-col">
                                                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Novas avaliações</span>
                                                    <span className="text-xs text-gray-500 dark:text-gray-400">Receba notificações quando novas avaliações forem atribuídas</span>
                                                </div>
                                                <div>
                                                    <input
                                                        type="checkbox"
                                                        defaultChecked
                                                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                                    />
                                                </div>
                                            </div>
                                            <div className="flex items-center justify-between">
                                                <div className="flex flex-col">
                                                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Lembretes de prazo</span>
                                                    <span className="text-xs text-gray-500 dark:text-gray-400">Receba lembretes quando prazos estiverem se aproximando</span>
                                                </div>
                                                <div>
                                                    <input
                                                        type="checkbox"
                                                        defaultChecked
                                                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                                    />
                                                </div>
                                            </div>
                                            <div className="flex items-center justify-between">
                                                <div className="flex flex-col">
                                                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Atualizações do sistema</span>
                                                    <span className="text-xs text-gray-500 dark:text-gray-400">Receba notificações sobre atualizações do sistema</span>
                                                </div>
                                                <div>
                                                    <input
                                                        type="checkbox"
                                                        defaultChecked
                                                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                                    />
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div>
                                        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Preferências de email</h3>
                                        <div className="flex items-center justify-between">
                                            <div className="flex flex-col">
                                                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Resumo diário</span>
                                                <span className="text-xs text-gray-500 dark:text-gray-400">Receba um resumo diário das atividades</span>
                                            </div>
                                            <div>
                                    <input
                                        type="checkbox"
                                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                    />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Data Tab */}
                        {activeTab === 'data' && (
                            <div className="p-6">
                                <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-5">Configurações de Dados</h2>

                                <div className="space-y-6">
                                    <div>
                                        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Fonte de dados</h3>
                                        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                                    URL do servidor
                                                </label>
                                                <input
                                                    type="text"
                                                    defaultValue="https://api.empresa.com"
                                                    className="mt-1 block w-full border border-gray-300 dark:border-gray-700 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white sm:text-sm"
                                                />
                                            </div>
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                                    Chave API
                                    </label>
                                                <input
                                                    type="password"
                                                    defaultValue="••••••••••••••••"
                                                    className="mt-1 block w-full border border-gray-300 dark:border-gray-700 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white sm:text-sm"
                                                />
                                            </div>
                                        </div>
                                    </div>

                                    <div>
                                        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Exportação de dados</h3>
                                        <div className="flex flex-col space-y-3 sm:flex-row sm:space-y-0 sm:space-x-3">
                                            <button className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-700 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700">
                                                Exportar CSV
                                            </button>
                                            <button className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-700 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700">
                                                Exportar JSON
                                            </button>
                                            <button className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-700 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700">
                                                Exportar Excel
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Advanced settings tab */}
                        {activeTab === 'advanced' && (
                            <div className="p-6">
                                <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-5">Configurações Avançadas</h2>

                                <div className="space-y-6">
                                    <div>
                                        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Cache e armazenamento</h3>
                                        <div className="flex flex-col space-y-3">
                                            <div className="flex items-center justify-between">
                                                <div className="flex flex-col">
                                                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Armazenamento local</span>
                                                    <span className="text-xs text-gray-500 dark:text-gray-400">10.4 MB</span>
                                                </div>
                                                <button className="inline-flex items-center px-3 py-1.5 border border-gray-300 dark:border-gray-700 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700">
                                                    Limpar
                                                </button>
                                            </div>
                                            <div className="flex items-center justify-between">
                                                <div className="flex flex-col">
                                                    <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Cache</span>
                                                    <span className="text-xs text-gray-500 dark:text-gray-400">2.1 MB</span>
                                                </div>
                                                <button className="inline-flex items-center px-3 py-1.5 border border-gray-300 dark:border-gray-700 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700">
                                                    Limpar
                                                </button>
                            </div>
                        </div>
                    </div>

                                    <div>
                                        <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Logs</h3>
                                        <button className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-700 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700">
                                            Exportar logs
                                        </button>
                                    </div>

                                    <div>
                                        <h3 className="text-sm font-medium text-red-600 dark:text-red-400 mb-3">Ações perigosas</h3>
                                        <button className="inline-flex items-center px-4 py-2 border border-red-300 dark:border-red-700 text-red-600 dark:text-red-400 rounded-md text-sm font-medium hover:bg-red-50 dark:hover:bg-red-900/20">
                                            Redefinir configurações
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Button row for all tabs */}
                        <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800/50">
                            <div className="flex justify-end">
                                <button className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 dark:hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-blue-400">
                                    <Save className="h-4 w-4 mr-2" />
                                    Salvar alterações
                        </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
} 