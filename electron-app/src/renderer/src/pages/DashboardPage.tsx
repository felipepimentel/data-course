import { Award, BarChart3, Calendar, ClipboardCheck, TrendingUp, UserCheck, Users } from 'lucide-react'

export function DashboardPage() {
    return (
        <div className="px-4 sm:px-6 lg:px-8 py-6">
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Análise geral de performance e desenvolvimento da equipe</p>
            </div>

            {/* KPI Summary Cards */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
                <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
                    <div className="p-5">
                        <div className="flex items-center">
                            <div className="flex-shrink-0 bg-blue-100 dark:bg-blue-900/30 rounded-md p-3">
                                <UserCheck className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                            </div>
                            <div className="ml-4">
                                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Colaboradores</p>
                                <div className="flex items-baseline">
                                    <p className="text-2xl font-semibold text-gray-900 dark:text-white">42</p>
                                    <p className="ml-2 text-sm font-medium text-green-600 dark:text-green-400">+3</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700/30 px-5 py-2">
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                            <span className="font-medium text-green-600 dark:text-green-400">+7.2%</span> vs mês anterior
                        </div>
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
                    <div className="p-5">
                        <div className="flex items-center">
                            <div className="flex-shrink-0 bg-purple-100 dark:bg-purple-900/30 rounded-md p-3">
                                <ClipboardCheck className="h-6 w-6 text-purple-600 dark:text-purple-400" />
                            </div>
                            <div className="ml-4">
                                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Avaliações Pendentes</p>
                                <div className="flex items-baseline">
                                    <p className="text-2xl font-semibold text-gray-900 dark:text-white">8</p>
                                    <p className="ml-2 text-sm font-medium text-red-600 dark:text-red-400">+2</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700/30 px-5 py-2">
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                            Próximo prazo: <span className="font-medium text-gray-900 dark:text-white">15/11</span>
                        </div>
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
                    <div className="p-5">
                        <div className="flex items-center">
                            <div className="flex-shrink-0 bg-green-100 dark:bg-green-900/30 rounded-md p-3">
                                <Award className="h-6 w-6 text-green-600 dark:text-green-400" />
                            </div>
                            <div className="ml-4">
                                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Score Médio</p>
                                <div className="flex items-baseline">
                                    <p className="text-2xl font-semibold text-gray-900 dark:text-white">7.8</p>
                                    <p className="ml-2 text-sm font-medium text-green-600 dark:text-green-400">+0.3</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700/30 px-5 py-2">
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                            <span className="font-medium text-green-600 dark:text-green-400">+4.1%</span> vs último trimestre
                        </div>
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
                    <div className="p-5">
                        <div className="flex items-center">
                            <div className="flex-shrink-0 bg-indigo-100 dark:bg-indigo-900/30 rounded-md p-3">
                                <TrendingUp className="h-6 w-6 text-indigo-600 dark:text-indigo-400" />
                            </div>
                            <div className="ml-4">
                                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">Promoções</p>
                                <div className="flex items-baseline">
                                    <p className="text-2xl font-semibold text-gray-900 dark:text-white">5</p>
                                    <p className="ml-2 text-sm font-medium text-green-600 dark:text-green-400">+2</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="bg-gray-50 dark:bg-gray-700/30 px-5 py-2">
                        <div className="text-sm text-gray-600 dark:text-gray-400">
                            Este trimestre
                        </div>
                    </div>
                </div>
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg p-6 border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center justify-between mb-5">
                        <h2 className="text-lg font-medium text-gray-900 dark:text-white">Distribuição de Avaliações</h2>
                        <div className="flex space-x-2">
                            <button className="px-3 py-1.5 text-xs font-medium bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400 rounded-md">Trimestral</button>
                            <button className="px-3 py-1.5 text-xs font-medium text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md">Anual</button>
                        </div>
                    </div>
                    <div className="flex items-center justify-center h-60 bg-gray-50 dark:bg-gray-700/30 rounded-lg">
                        <div className="flex flex-col items-center text-gray-500 dark:text-gray-400">
                            <BarChart3 className="h-12 w-12 mb-2" />
                            <p className="text-sm font-medium">Gráfico de Distribuição de Avaliações</p>
                        </div>
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg p-6 border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center justify-between mb-5">
                        <h2 className="text-lg font-medium text-gray-900 dark:text-white">Crescimento de Habilidades</h2>
                        <div className="flex space-x-2">
                            <button className="px-3 py-1.5 text-xs font-medium bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400 rounded-md">6 meses</button>
                            <button className="px-3 py-1.5 text-xs font-medium text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md">12 meses</button>
                        </div>
                    </div>
                    <div className="flex items-center justify-center h-60 bg-gray-50 dark:bg-gray-700/30 rounded-lg">
                        <div className="flex flex-col items-center text-gray-500 dark:text-gray-400">
                            <BarChart3 className="h-12 w-12 mb-2" />
                            <p className="text-sm font-medium">Gráfico de Crescimento de Habilidades</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Team Section */}
            <div className="mb-8">
                <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
                    <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                        <div className="flex items-center justify-between">
                            <h2 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
                                <Users className="h-5 w-5 mr-2 text-gray-500 dark:text-gray-400" />
                                Membros do Time
                            </h2>
                            <button className="px-3 py-1.5 text-xs font-medium text-blue-600 dark:text-blue-400 border border-blue-500 dark:border-blue-400 rounded-md hover:bg-blue-50 dark:hover:bg-blue-900/20">
                                Ver Todos
                            </button>
                        </div>
                    </div>
                    <div className="p-5">
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                                <thead>
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Nome</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Cargo</th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Departamento</th>
                                        <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Score</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                                    <tr>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <div className="h-8 w-8 rounded-full bg-gradient-to-r from-blue-500 to-teal-500 flex items-center justify-center text-white font-bold text-xs">JS</div>
                                                <div className="ml-4">
                                                    <div className="text-sm font-medium text-gray-900 dark:text-white">João Silva</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">Tech Lead</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">Engenharia</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-green-600 dark:text-green-400">8.7</td>
                                    </tr>
                                    <tr>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <div className="h-8 w-8 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-xs">MC</div>
                                                <div className="ml-4">
                                                    <div className="text-sm font-medium text-gray-900 dark:text-white">Maria Costa</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">UX Designer</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">Design</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-green-600 dark:text-green-400">9.2</td>
                                    </tr>
                                    <tr>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center">
                                                <div className="h-8 w-8 rounded-full bg-gradient-to-r from-amber-500 to-orange-500 flex items-center justify-center text-white font-bold text-xs">PL</div>
                                                <div className="ml-4">
                                                    <div className="text-sm font-medium text-gray-900 dark:text-white">Pedro Lima</div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">Desenvolvedor</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">Engenharia</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-right font-medium text-yellow-600 dark:text-yellow-400">6.5</td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>

            {/* Calendar & Upcoming Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
                    <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                        <div className="flex items-center justify-between">
                            <h2 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
                                <Calendar className="h-5 w-5 mr-2 text-gray-500 dark:text-gray-400" />
                                Próximas Avaliações
                            </h2>
                        </div>
                    </div>
                    <div className="p-5">
                        <ul className="space-y-4">
                            <li className="flex items-start">
                                <div className="flex-shrink-0 h-10 w-10 rounded-md bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center text-blue-600 dark:text-blue-400 font-medium">
                                    15
                                    <span className="text-xs">Nov</span>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-900 dark:text-white">Avaliação Trimestral - Time de Desenvolvimento</p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">8 colaboradores pendentes</p>
                                </div>
                            </li>
                            <li className="flex items-start">
                                <div className="flex-shrink-0 h-10 w-10 rounded-md bg-purple-100 dark:bg-purple-900/30 flex items-center justify-center text-purple-600 dark:text-purple-400 font-medium">
                                    22
                                    <span className="text-xs">Nov</span>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-900 dark:text-white">Feedback 360° - Lideranças</p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">5 líderes participantes</p>
                                </div>
                            </li>
                            <li className="flex items-start">
                                <div className="flex-shrink-0 h-10 w-10 rounded-md bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600 dark:text-green-400 font-medium">
                                    05
                                    <span className="text-xs">Dez</span>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-900 dark:text-white">Revisão de Metas - Marketing</p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">4 colaboradores pendentes</p>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>

                <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
                    <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                        <div className="flex items-center justify-between">
                            <h2 className="text-lg font-medium text-gray-900 dark:text-white flex items-center">
                                <TrendingUp className="h-5 w-5 mr-2 text-gray-500 dark:text-gray-400" />
                                Destaques de Performance
                            </h2>
                        </div>
                    </div>
                    <div className="p-5">
                        <div className="space-y-4">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center">
                                    <div className="h-10 w-10 rounded-full bg-gradient-to-r from-blue-500 to-teal-500 flex items-center justify-center text-white font-bold text-xs">
                                        AC
                                    </div>
                                    <div className="ml-3">
                                        <p className="text-sm font-medium text-gray-900 dark:text-white">Ana Claudia</p>
                                        <p className="text-xs text-gray-500 dark:text-gray-400">Maior crescimento técnico</p>
                                    </div>
                                </div>
                                <div className="flex items-center px-3 py-1.5 bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 text-xs font-medium rounded-full">
                                    +42%
                                </div>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center">
                                    <div className="h-10 w-10 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-xs">
                                        RB
                                    </div>
                                    <div className="ml-3">
                                        <p className="text-sm font-medium text-gray-900 dark:text-white">Roberto Barros</p>
                                        <p className="text-xs text-gray-500 dark:text-gray-400">Melhor nota em liderança</p>
                                    </div>
                                </div>
                                <div className="flex items-center px-3 py-1.5 bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 text-xs font-medium rounded-full">
                                    9.8
                                </div>
                            </div>
                            <div className="flex items-center justify-between">
                                <div className="flex items-center">
                                    <div className="h-10 w-10 rounded-full bg-gradient-to-r from-amber-500 to-orange-500 flex items-center justify-center text-white font-bold text-xs">
                                        LF
                                    </div>
                                    <div className="ml-3">
                                        <p className="text-sm font-medium text-gray-900 dark:text-white">Luciana Ferreira</p>
                                        <p className="text-xs text-gray-500 dark:text-gray-400">Maior satisfação da equipe</p>
                                    </div>
                                </div>
                                <div className="flex items-center px-3 py-1.5 bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 text-xs font-medium rounded-full">
                                    4.9/5
                                </div>
                            </div>
                        </div>
                </div>
                </div>
            </div>
        </div>
    )
} 