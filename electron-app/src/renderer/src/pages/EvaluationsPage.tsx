import { Check, ChevronDown, ChevronUp, ClipboardCheck, Clock, Download, Edit, Filter, Plus, Search, Star, Trash, User, ArrowLeft, Calendar, BookOpen, Award, Activity, Coffee, Mail, Phone, MapPin } from 'lucide-react'
import React, { useState, useEffect } from 'react'

type EvaluationStatus = 'pending' | 'in_progress' | 'completed'
type SortDirection = 'asc' | 'desc'
type ViewMode = 'list' | 'user-profile' | 'people-list'

interface SortConfig {
    key: string
    direction: SortDirection
}

// Adicionar interface para detalhes da avaliação
interface EvaluationDetail {
    id: number
    year: string
    quarter: string
    indicators: {
        name: string
        score: number
        weight: number
        comments: string
    }[]
    overallComments: string
    developmentPlan: string
}

interface UserProfile {
    id: number
    name: string
    role: string
    department: string
    email: string
    phone: string
    manager: string
    hireDate: string
    location: string
    bio: string
    skills: string[]
    evaluationHistory: EvaluationDetail[]
}

interface EvaluationsPageProps {
    initialViewMode?: ViewMode
}

export function EvaluationsPage({ initialViewMode = 'list' }: EvaluationsPageProps) {
    const [activeTab, setActiveTab] = useState<'pendentes' | 'concluidas'>('pendentes')
    const [selectedDepartment, setSelectedDepartment] = useState<string>('Todos')
    const [isFilterOpen, setIsFilterOpen] = useState(false)
    const [searchTerm, setSearchTerm] = useState<string>('')
    const [sortConfig, setSortConfig] = useState<SortConfig>({ key: '', direction: 'asc' })

    // Estado para navegação por usuário
    const [viewMode, setViewMode] = useState<ViewMode>(initialViewMode)
    const [selectedUser, setSelectedUser] = useState<UserProfile | null>(null)
    const [selectedYear, setSelectedYear] = useState<string>('2023')

    // Definir o viewMode baseado na prop initialViewMode
    useEffect(() => {
        setViewMode(initialViewMode);
    }, [initialViewMode]);

    // Mock data
    const pendingEvaluations = [
        { id: 1, name: 'João Silva', department: 'Engenharia', role: 'Tech Lead', dueDate: '15/11/2023', status: 'pending' },
        { id: 2, name: 'Maria Costa', department: 'Design', role: 'UX Designer', dueDate: '15/11/2023', status: 'pending' },
        { id: 3, name: 'Pedro Lima', department: 'Engenharia', role: 'Desenvolvedor', dueDate: '15/11/2023', status: 'in_progress' },
        { id: 4, name: 'Ana Claudia', department: 'Marketing', role: 'Marketing Manager', dueDate: '22/11/2023', status: 'pending' },
        { id: 5, name: 'Roberto Barros', department: 'Produto', role: 'Product Owner', dueDate: '22/11/2023', status: 'in_progress' }
    ]

    const completedEvaluations = [
        { id: 6, name: 'Luciana Ferreira', department: 'RH', role: 'Gerente de RH', evaluationDate: '10/08/2023', score: 9.2 },
        { id: 7, name: 'Carlos Mendes', department: 'Engenharia', role: 'CTO', evaluationDate: '05/08/2023', score: 8.5 },
        { id: 8, name: 'Juliana Santos', department: 'Financeiro', role: 'Analista Financeiro', evaluationDate: '01/08/2023', score: 7.8 },
        { id: 9, name: 'Marcos Oliveira', department: 'Marketing', role: 'Designer Gráfico', evaluationDate: '28/07/2023', score: 8.1 },
        { id: 10, name: 'Patricia Alves', department: 'Vendas', role: 'Gerente de Vendas', evaluationDate: '25/07/2023', score: 9.0 }
    ]

    const departments = ['Todos', 'Engenharia', 'Design', 'Marketing', 'Produto', 'RH', 'Financeiro', 'Vendas']

    // Mock data para detalhes de avaliação
    const mockEvaluationDetails: Record<number, EvaluationDetail[]> = {
        6: [
            {
                id: 601,
                year: "2023",
                quarter: "Q3",
                indicators: [
                    { name: "Gestão de Equipe", score: 9.5, weight: 0.3, comments: "Excelente liderança e comunicação com a equipe" },
                    { name: "Processos de RH", score: 9.0, weight: 0.4, comments: "Implementou novos processos que melhoraram a eficiência do departamento" },
                    { name: "Cultura Organizacional", score: 9.2, weight: 0.3, comments: "Contribuiu ativamente para fortalecer a cultura da empresa" }
                ],
                overallComments: "Luciana tem apresentado um desempenho excepcional na gestão do departamento de RH, com iniciativas inovadoras e forte liderança.",
                developmentPlan: "Participação em treinamento avançado de gestão de conflitos e desenvolvimento de habilidades em people analytics."
            },
            {
                id: 602,
                year: "2022",
                quarter: "Q4",
                indicators: [
                    { name: "Gestão de Equipe", score: 8.5, weight: 0.3, comments: "Boa gestão da equipe, com oportunidades de melhoria na delegação" },
                    { name: "Processos de RH", score: 8.8, weight: 0.4, comments: "Processos eficientes, mas com espaço para automação" },
                    { name: "Cultura Organizacional", score: 9.0, weight: 0.3, comments: "Forte contribuição para a cultura" }
                ],
                overallComments: "Desempenho sólido ao longo do ano, com melhorias consistentes em áreas-chave.",
                developmentPlan: "Foco em automação de processos de RH e desenvolvimento de habilidades de mentoria."
            }
        ],
        7: [
            {
                id: 701,
                year: "2023",
                quarter: "Q3",
                indicators: [
                    { name: "Liderança Técnica", score: 8.7, weight: 0.4, comments: "Forte liderança técnica e direcionamento da equipe" },
                    { name: "Inovação", score: 8.2, weight: 0.3, comments: "Implementou novas tecnologias que melhoraram a escalabilidade" },
                    { name: "Gestão de Projetos", score: 8.6, weight: 0.3, comments: "Boa gestão de projetos, cumprindo a maioria dos prazos" }
                ],
                overallComments: "Carlos demonstrou excelente capacidade técnica e visão estratégica para o departamento de tecnologia.",
                developmentPlan: "Aprimoramento em metodologias ágeis e desenvolvimento de soft skills para comunicação com outras áreas."
            }
        ]
    }

    // Função para buscar detalhes da avaliação
    const fetchEvaluationDetails = (evaluationId: number) => {
        // Em um cenário real, isso seria uma chamada API
        // Retornando os dados mockados para demonstração
        return mockEvaluationDetails[evaluationId] || [];
    }

    // Função para abrir os detalhes da avaliação
    const openEvaluationDetails = (evaluation: any) => {
        setSelectedEvaluation(evaluation);
        const details = fetchEvaluationDetails(evaluation.id);
        setEvaluationDetails(details.find(d => d.year === selectedYear) || details[0] || null);
        setShowDetails(true);
    }

    // Função para alterar o ano visualizado
    const changeYear = (year: string) => {
        setSelectedYear(year);
        if (selectedEvaluation) {
            const details = fetchEvaluationDetails(selectedEvaluation.id);
            setEvaluationDetails(details.find(d => d.year === year) || null);
        }
    }

    const getStatusBadge = (status: string) => {
        if (status === 'pending') {
            return (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-500">
                    <Clock className="mr-1 h-3 w-3" />
                    Pendente
                </span>
            )
        } else if (status === 'in_progress') {
            return (
                <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-500">
                    <Clock className="mr-1 h-3 w-3" />
                    Em progresso
                </span>
            )
        }
        return null
    }

    const getScoreBadge = (score: number) => {
        let colorClass = 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-500'
        if (score < 6) {
            colorClass = 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-500'
        } else if (score < 8) {
            colorClass = 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-500'
        }

        return (
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
                <Star className="mr-1 h-3 w-3" />
                {score}
            </span>
        )
    }

    const handleSort = (key: string) => {
        let direction: SortDirection = 'asc'
        if (sortConfig.key === key && sortConfig.direction === 'asc') {
            direction = 'desc'
        }
        setSortConfig({ key, direction })
    }

    const getSortIcon = (columnName: string) => {
        if (sortConfig.key !== columnName) {
            return null
        }
        return sortConfig.direction === 'asc'
            ? <ChevronUp className="h-4 w-4 ml-1" />
            : <ChevronDown className="h-4 w-4 ml-1" />
    }

    const sortedPendingEvaluations = React.useMemo(() => {
        const sortableItems = [...pendingEvaluations]
        if (sortConfig.key) {
            sortableItems.sort((a: any, b: any) => {
                if (a[sortConfig.key] < b[sortConfig.key]) {
                    return sortConfig.direction === 'asc' ? -1 : 1
                }
                if (a[sortConfig.key] > b[sortConfig.key]) {
                    return sortConfig.direction === 'asc' ? 1 : -1
                }
                return 0
            })
        }
        return sortableItems
    }, [pendingEvaluations, sortConfig])

    const sortedCompletedEvaluations = React.useMemo(() => {
        const sortableItems = [...completedEvaluations]
        if (sortConfig.key) {
            sortableItems.sort((a: any, b: any) => {
                if (a[sortConfig.key] < b[sortConfig.key]) {
                    return sortConfig.direction === 'asc' ? -1 : 1
                }
                if (a[sortConfig.key] > b[sortConfig.key]) {
                    return sortConfig.direction === 'asc' ? 1 : -1
                }
                return 0
            })
        }
        return sortableItems
    }, [completedEvaluations, sortConfig])

    const filteredPendingEvaluations = sortedPendingEvaluations.filter(item =>
        (selectedDepartment === 'Todos' || item.department === selectedDepartment) &&
        (searchTerm === '' ||
            item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.department.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.role.toLowerCase().includes(searchTerm.toLowerCase()))
    )

    const filteredCompletedEvaluations = sortedCompletedEvaluations.filter(item =>
        (selectedDepartment === 'Todos' || item.department === selectedDepartment) &&
        (searchTerm === '' ||
            item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.department.toLowerCase().includes(searchTerm.toLowerCase()) ||
            item.role.toLowerCase().includes(searchTerm.toLowerCase()))
    )

    const clearFilters = () => {
        setSearchTerm('')
        setSelectedDepartment('Todos')
        setSortConfig({ key: '', direction: 'asc' })
    }

    const TableHeader = ({ label, sortKey }: { label: string, sortKey?: string }) => (
        <th
            className={`px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider ${sortKey ? 'cursor-pointer hover:text-gray-700 dark:hover:text-gray-300' : ''}`}
            onClick={() => sortKey && handleSort(sortKey)}
        >
            {sortKey ? (
                <div className="flex items-center">
                    {label}
                    {getSortIcon(sortKey)}
                </div>
            ) : label}
        </th>
    )

    // Calcular o score ponderado
    const calculateWeightedScore = (details: EvaluationDetail | null) => {
        if (!details) return 0;

        return details.indicators.reduce((total, indicator) => {
            return total + (indicator.score * indicator.weight);
        }, 0).toFixed(1);
    }

    // Função para voltar da visão de detalhes do usuário
    const backToList = () => {
        if (initialViewMode === 'user-profile' || initialViewMode === 'people-list') {
            // Se estamos na rota /people, permanecemos na visão de pessoas
            setViewMode('people-list');
            setSelectedUser(null);
        } else {
            // Se estamos na rota /evaluations, voltamos para a lista de avaliações
            setViewMode('list');
            setSelectedUser(null);
        }
    }

    // Lista de todos os perfis de usuário para a visualização de pessoas
    const allUserProfiles = Object.values(userProfiles);

    return (
        <div className="px-4 sm:px-6 lg:px-8 py-8">
            {viewMode === 'list' ? (
                // Lista de avaliações (UI existente)
                <>
                    <div className="mb-8">
                        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Avaliações</h1>
                        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Gerencie avaliações de desempenho da sua equipe</p>
                    </div>

                    {/* Action Bar */}
                    <div className="mb-6 flex flex-col sm:flex-row justify-between gap-4">
                        <div className="w-full sm:max-w-xs">
                            <div className="relative rounded-md shadow-sm">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Search className="h-5 w-5 text-gray-400" />
                                </div>
                                <input
                                    type="text"
                                    placeholder="Buscar avaliações..."
                                    value={searchTerm}
                                    onChange={(e) => setSearchTerm(e.target.value)}
                                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:placeholder-gray-400 dark:focus:placeholder-gray-500 focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500 dark:focus:border-blue-400 sm:text-sm"
                                />
                            </div>
                        </div>
                        <div className="flex flex-col sm:flex-row gap-3 sm:items-center">
                            <div className="relative">
                                <button
                                    className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-md inline-flex items-center shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-100 dark:focus:ring-offset-gray-800 focus:ring-blue-500 dark:focus:ring-blue-400"
                                    onClick={() => setIsFilterOpen(!isFilterOpen)}
                                >
                                    <Filter className="h-4 w-4 mr-2" />
                                    Filtrar
                                    <ChevronDown className="ml-2 h-4 w-4" />
                                </button>
                                {isFilterOpen && (
                                    <div className="origin-top-right absolute right-0 mt-2 w-48 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 z-10 border border-gray-200 dark:border-gray-700">
                                        <div className="py-1" role="menu" aria-orientation="vertical">
                                            <div className="px-4 py-2 text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                                                Departamento
                                            </div>
                                            {departments.map((dept) => (
                                                <button
                                                    key={dept}
                                                    className={`block px-4 py-2 text-sm w-full text-left ${selectedDepartment === dept
                                                        ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'
                                                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                                                        }`}
                                                    onClick={() => {
                                                        setSelectedDepartment(dept)
                                                        setIsFilterOpen(false)
                                                    }}
                                                >
                                                    {dept}
                                                    {selectedDepartment === dept && <Check className="float-right h-4 w-4" />}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                            {(searchTerm !== '' || selectedDepartment !== 'Todos' || sortConfig.key !== '') && (
                                <button
                                    onClick={clearFilters}
                                    className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-700 rounded-md inline-flex items-center shadow-sm hover:bg-gray-50 dark:hover:bg-gray-700"
                                >
                                    Limpar Filtros
                                </button>
                            )}
                            <button className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 dark:hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-blue-400">
                                <Plus className="h-4 w-4 mr-2" />
                                Nova Avaliação
                            </button>
                            <button className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-700 shadow-sm text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-blue-400">
                                <Download className="h-4 w-4 mr-2" />
                                Exportar
                            </button>
                        </div>
                    </div>

                    {/* Tabs */}
                    <div className="border-b border-gray-200 dark:border-gray-700 mb-6">
                        <nav className="-mb-px flex" aria-label="Tabs">
                            <button
                                className={`py-4 px-1 border-b-2 font-medium text-sm mr-8 ${activeTab === 'pendentes'
                                    ? 'border-blue-500 text-blue-600 dark:border-blue-400 dark:text-blue-400'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:border-gray-600'
                                    }`}
                                onClick={() => setActiveTab('pendentes')}
                            >
                                Pendentes <span className="ml-2 py-0.5 px-2 rounded-full text-xs bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-500">{filteredPendingEvaluations.length}</span>
                            </button>
                            <button
                                className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'concluidas'
                                    ? 'border-blue-500 text-blue-600 dark:border-blue-400 dark:text-blue-400'
                                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400 dark:hover:text-gray-300 dark:hover:border-gray-600'
                                    }`}
                                onClick={() => setActiveTab('concluidas')}
                            >
                                Concluídas <span className="ml-2 py-0.5 px-2 rounded-full text-xs bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300">{filteredCompletedEvaluations.length}</span>
                            </button>
                        </nav>
                    </div>

                    {/* Empty State */}
                    {activeTab === 'pendentes' && filteredPendingEvaluations.length === 0 && (
                        <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg p-8 text-center border border-gray-200 dark:border-gray-700">
                            <div className="mx-auto h-12 w-12 text-gray-400 mb-4">
                                <ClipboardCheck className="h-12 w-12" />
                            </div>
                            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Nenhuma avaliação pendente encontrada</h3>
                            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                                {searchTerm || selectedDepartment !== 'Todos'
                                    ? 'Tente ajustar seus filtros para ver mais resultados.'
                                    : 'Todas as avaliações foram concluídas. Crie uma nova avaliação para começar.'}
                            </p>
                            <div className="mt-6">
                                <button
                                    type="button"
                                    className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 dark:hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-blue-400"
                                >
                                    <Plus className="h-4 w-4 mr-2" />
                                    Nova Avaliação
                                </button>
                            </div>
                        </div>
                    )}

                    {activeTab === 'concluidas' && filteredCompletedEvaluations.length === 0 && (
                        <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg p-8 text-center border border-gray-200 dark:border-gray-700">
                            <div className="mx-auto h-12 w-12 text-gray-400 mb-4">
                                <ClipboardCheck className="h-12 w-12" />
                            </div>
                            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Nenhuma avaliação concluída encontrada</h3>
                            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                                {searchTerm || selectedDepartment !== 'Todos'
                                    ? 'Tente ajustar seus filtros para ver mais resultados.'
                                    : 'Nenhuma avaliação foi concluída ainda.'}
                            </p>
                        </div>
                    )}

                    {/* Table for Pending Evaluations */}
                    {activeTab === 'pendentes' && filteredPendingEvaluations.length > 0 && (
                        <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
                            <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                                    <thead>
                                        <tr>
                                            <TableHeader label="Colaborador" sortKey="name" />
                                            <TableHeader label="Departamento" sortKey="department" />
                                            <TableHeader label="Cargo" sortKey="role" />
                                            <TableHeader label="Data Limite" sortKey="dueDate" />
                                            <TableHeader label="Status" sortKey="status" />
                                            <TableHeader label="Ações" />
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                                        {filteredPendingEvaluations.map((evaluation) => (
                                            <tr key={evaluation.id}>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <div className="flex items-center">
                                                        <div className="h-8 w-8 rounded-full bg-gradient-to-r from-blue-500 to-teal-500 flex items-center justify-center text-white font-bold text-xs">
                                                            {evaluation.name.split(' ').map(n => n[0]).join('')}
                                                        </div>
                                                        <div className="ml-4">
                                                            <div className="text-sm font-medium text-gray-900 dark:text-white">{evaluation.name}</div>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">{evaluation.department}</td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">{evaluation.role}</td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">{evaluation.dueDate}</td>
                                                <td className="px-6 py-4 whitespace-nowrap">{getStatusBadge(evaluation.status)}</td>
                                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                    <button className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 mr-4">
                                                        Avaliar
                                                    </button>
                                                    <button className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">
                                                        <Trash className="h-4 w-4" />
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {/* Table for Completed Evaluations */}
                    {activeTab === 'concluidas' && filteredCompletedEvaluations.length > 0 && (
                        <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700">
                            <div className="overflow-x-auto">
                                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                                    <thead>
                                        <tr>
                                            <TableHeader label="Colaborador" sortKey="name" />
                                            <TableHeader label="Departamento" sortKey="department" />
                                            <TableHeader label="Cargo" sortKey="role" />
                                            <TableHeader label="Data Avaliação" sortKey="evaluationDate" />
                                            <TableHeader label="Score" sortKey="score" />
                                            <TableHeader label="Ações" />
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                                        {filteredCompletedEvaluations.map((evaluation) => (
                                            <tr key={evaluation.id}>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <div className="flex items-center">
                                                        <div className="h-8 w-8 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-xs">
                                                            {evaluation.name.split(' ').map(n => n[0]).join('')}
                                                        </div>
                                                        <div className="ml-4">
                                                            <div className="text-sm font-medium text-gray-900 dark:text-white">{evaluation.name}</div>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">{evaluation.department}</td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">{evaluation.role}</td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 dark:text-gray-400">{evaluation.evaluationDate}</td>
                                                <td className="px-6 py-4 whitespace-nowrap">{getScoreBadge(evaluation.score)}</td>
                                                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                                    <button
                                                        onClick={() => openEvaluationDetails(evaluation)}
                                                        className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 mr-4"
                                                    >
                                                        Ver Detalhes
                                                    </button>
                                                    <button className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300 mr-4">
                                                        <Edit className="h-4 w-4" />
                                                    </button>
                                                    <button className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300">
                                                        <Download className="h-4 w-4" />
                                                    </button>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}

                    {/* Modal de Detalhes da Avaliação */}
                    {showDetails && selectedEvaluation && (
                        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-20 p-4">
                            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
                                <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700">
                                    <div>
                                        <h2 className="text-xl font-bold text-gray-900 dark:text-white flex items-center">
                                            Avaliação de {selectedEvaluation.name}
                                            <span className="ml-3">{getScoreBadge(selectedEvaluation.score)}</span>
                                        </h2>
                                        <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                            {selectedEvaluation.department} • {selectedEvaluation.role}
                                        </p>
                                    </div>
                                    <button
                                        onClick={() => setShowDetails(false)}
                                        className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300"
                                    >
                                        <X className="h-6 w-6" />
                                    </button>
                                </div>

                                {/* Seletor de Ano */}
                                <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                                    <div className="flex space-x-2">
                                        {['2023', '2022', '2021'].map(year => (
                                            <button
                                                key={year}
                                                className={`px-4 py-2 rounded-md text-sm font-medium ${selectedYear === year
                                                    ? 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
                                                    : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                                                    }`}
                                                onClick={() => changeYear(year)}
                                            >
                                                {year}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                {evaluationDetails ? (
                                    <div className="p-6">
                                        <div className="mb-8">
                                            <div className="flex justify-between items-center mb-4">
                                                <h3 className="text-lg font-medium text-gray-900 dark:text-white">Indicadores de Desempenho</h3>
                                                <span className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                                                    {calculateWeightedScore(evaluationDetails)}
                                                </span>
                                            </div>

                                            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-6">
                                                <div className="grid gap-4">
                                                    {evaluationDetails.indicators.map((indicator, index) => (
                                                        <div key={index} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-sm">
                                                            <div className="flex justify-between items-center mb-2">
                                                                <h4 className="font-medium text-gray-900 dark:text-white">{indicator.name}</h4>
                                                                <div className="flex items-center">
                                                                    <span className="text-sm text-gray-500 dark:text-gray-400 mr-2">
                                                                        Peso: {indicator.weight * 100}%
                                                                    </span>
                                                                    <span className="font-bold text-lg text-blue-600 dark:text-blue-400">
                                                                        {indicator.score.toFixed(1)}
                                                                    </span>
                                                                </div>
                                                            </div>
                                                            <p className="text-sm text-gray-600 dark:text-gray-400">{indicator.comments}</p>
                                                        </div>
                                                    ))}
                                                </div>
                                            </div>
                                        </div>

                                        <div className="mb-8">
                                            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Comentários Gerais</h3>
                                            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                                                <p className="text-gray-700 dark:text-gray-300">{evaluationDetails.overallComments}</p>
                                            </div>
                                        </div>

                                        <div>
                                            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Plano de Desenvolvimento</h3>
                                            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                                                <p className="text-gray-700 dark:text-gray-300">{evaluationDetails.developmentPlan}</p>
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    <div className="p-6 text-center">
                                        <p className="text-gray-600 dark:text-gray-400">Não há dados de avaliação disponíveis para o ano selecionado.</p>
                                    </div>
                                )}

                                <div className="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end">
                                    <button
                                        onClick={() => setShowDetails(false)}
                                        className="px-4 py-2 bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-md text-sm font-medium mr-2"
                                    >
                                        Fechar
                                    </button>
                                    <button className="px-4 py-2 bg-blue-600 text-white dark:bg-blue-500 hover:bg-blue-700 dark:hover:bg-blue-600 rounded-md text-sm font-medium">
                                        <Download className="h-4 w-4 mr-2 inline-block" />
                                        Exportar PDF
                                    </button>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            )
}