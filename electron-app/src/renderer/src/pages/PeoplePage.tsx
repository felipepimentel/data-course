import { Check, ChevronDown, Filter, Mail, Plus, Search, User } from 'lucide-react'
import { useState } from 'react'

// Tipos e interfaces
type SortDirection = 'asc' | 'desc'

interface SortConfig {
    key: string
    direction: SortDirection
}

interface UserProfile {
    id: number
    name: string
    email: string
    phone: string
    department: string
    role: string
    location: string
    hireDate: string
    manager: string
    avatar?: string
    bio: string
    skills: string[]
    evaluationHistory: {
        year: string
        quarter: string
        score: number
        evaluationDate: string
        indicators: {
            name: string
            score: number
            weight: number
        }[]
    }[]
}

export function PeoplePage() {
    const [selectedDepartment, setSelectedDepartment] = useState<string>('Todos')
    const [isFilterOpen, setIsFilterOpen] = useState(false)
    const [searchTerm, setSearchTerm] = useState<string>('')
    const [sortConfig, setSortConfig] = useState<SortConfig>({ key: 'name', direction: 'asc' })
    const [selectedUser, setSelectedUser] = useState<UserProfile | null>(null)

    // Mock data para departamentos
    const departments = ['Todos', 'Engenharia', 'Design', 'Marketing', 'Produto', 'RH', 'Financeiro', 'Vendas']

    // Mock data para perfis de usuários
    const userProfiles: Record<number, UserProfile> = {
        6: {
            id: 6,
            name: 'Luciana Ferreira',
            email: 'luciana.ferreira@empresa.com',
            phone: '+55 (11) 98765-4321',
            department: 'RH',
            role: 'Gerente de RH',
            location: 'São Paulo, SP',
            hireDate: '15/03/2019',
            manager: 'Roberto Santana',
            bio: 'Profissional de RH com mais de 10 anos de experiência em gestão de pessoas e desenvolvimento organizacional. Especialista em cultura organizacional e programas de desenvolvimento de liderança.',
            skills: ['Gestão de Pessoas', 'Recrutamento e Seleção', 'Desenvolvimento Organizacional', 'Treinamento', 'Cultura Organizacional'],
            evaluationHistory: [
                {
                    year: '2023',
                    quarter: 'Q3',
                    score: 9.2,
                    evaluationDate: '10/08/2023',
                    indicators: [
                        { name: 'Gestão de Equipe', score: 9.5, weight: 0.3 },
                        { name: 'Processos de RH', score: 9.0, weight: 0.4 },
                        { name: 'Cultura Organizacional', score: 9.2, weight: 0.3 }
                    ]
                },
                {
                    year: '2022',
                    quarter: 'Q4',
                    score: 8.7,
                    evaluationDate: '12/11/2022',
                    indicators: [
                        { name: 'Gestão de Equipe', score: 8.5, weight: 0.3 },
                        { name: 'Processos de RH', score: 8.8, weight: 0.4 },
                        { name: 'Cultura Organizacional', score: 8.7, weight: 0.3 }
                    ]
                }
            ]
        },
        7: {
            id: 7,
            name: 'Carlos Mendes',
            email: 'carlos.mendes@empresa.com',
            phone: '+55 (11) 97654-3210',
            department: 'Engenharia',
            role: 'CTO',
            location: 'São Paulo, SP',
            hireDate: '05/01/2018',
            manager: 'Fernando Costa (CEO)',
            bio: 'Engenheiro de software com experiência em liderança técnica e desenvolvimento de produtos. Especialista em arquitetura de sistemas distribuídos e desenvolvimento ágil.',
            skills: ['Arquitetura de Software', 'Liderança Técnica', 'Cloud Computing', 'DevOps', 'Gestão de Produtos'],
            evaluationHistory: [
                {
                    year: '2023',
                    quarter: 'Q3',
                    score: 8.5,
                    evaluationDate: '05/08/2023',
                    indicators: [
                        { name: 'Liderança Técnica', score: 8.7, weight: 0.4 },
                        { name: 'Inovação', score: 8.2, weight: 0.3 },
                        { name: 'Gestão de Projetos', score: 8.6, weight: 0.3 }
                    ]
                },
                {
                    year: '2022',
                    quarter: 'Q4',
                    score: 8.3,
                    evaluationDate: '10/11/2022',
                    indicators: [
                        { name: 'Liderança Técnica', score: 8.4, weight: 0.4 },
                        { name: 'Inovação', score: 8.0, weight: 0.3 },
                        { name: 'Gestão de Projetos', score: 8.5, weight: 0.3 }
                    ]
                }
            ]
        },
        8: {
            id: 8,
            name: 'Juliana Santos',
            email: 'juliana.santos@empresa.com',
            phone: '+55 (11) 91234-5678',
            department: 'Financeiro',
            role: 'Analista Financeiro',
            location: 'São Paulo, SP',
            hireDate: '10/05/2020',
            manager: 'Marcelo Ribeiro',
            bio: 'Analista financeira com experiência em planejamento financeiro e análise de investimentos. Especialista em modelagem financeira e valuation.',
            skills: ['Análise Financeira', 'Planejamento Financeiro', 'Excel Avançado', 'Valuation', 'Relatórios Gerenciais'],
            evaluationHistory: [
                {
                    year: '2023',
                    quarter: 'Q3',
                    score: 7.8,
                    evaluationDate: '01/08/2023',
                    indicators: [
                        { name: 'Análise Financeira', score: 8.0, weight: 0.4 },
                        { name: 'Relatórios', score: 7.5, weight: 0.3 },
                        { name: 'Trabalho em Equipe', score: 7.9, weight: 0.3 }
                    ]
                }
            ]
        }
    }

    // Helper para obter o score badge
    const getScoreBadge = (score: number) => {
        let colorClass = 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-500'
        if (score < 6) {
            colorClass = 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-500'
        } else if (score < 8) {
            colorClass = 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-500'
        }

        return (
            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
                {score.toFixed(1)}
            </span>
        )
    }

    // Lista de todos os perfis de usuário
    const allUserProfiles = Object.values(userProfiles)

    // Perfis filtrados
    const filteredProfiles = allUserProfiles.filter(profile =>
        (selectedDepartment === 'Todos' || profile.department === selectedDepartment) &&
        (searchTerm === '' ||
            profile.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            profile.department.toLowerCase().includes(searchTerm.toLowerCase()) ||
            profile.role.toLowerCase().includes(searchTerm.toLowerCase()))
    ).sort((a, b) => {
        const key = sortConfig.key as keyof UserProfile
        if (typeof a[key] === 'string' && typeof b[key] === 'string') {
            return sortConfig.direction === 'asc'
                ? (a[key] as string).localeCompare(b[key] as string)
                : (b[key] as string).localeCompare(a[key] as string)
        }
        return 0
    })

    return (
        <div className="px-4 sm:px-6 lg:px-8 py-8">
            {!selectedUser ? (
                <>
                    <div className="mb-8">
                        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Pessoas</h1>
                        <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">Visualize e gerencie os perfis dos colaboradores</p>
                    </div>

                    {/* Barra de pesquisa e filtros */}
                    <div className="mb-6 flex flex-col sm:flex-row justify-between gap-4">
                        <div className="w-full sm:max-w-xs">
                            <div className="relative rounded-md shadow-sm">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <Search className="h-5 w-5 text-gray-400" />
                                </div>
                                <input
                                    type="text"
                                    placeholder="Buscar pessoas..."
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
                            <button className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 dark:bg-blue-500 hover:bg-blue-700 dark:hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 dark:focus:ring-blue-400">
                                <Plus className="h-4 w-4 mr-2" />
                                Nova Pessoa
                            </button>
                        </div>
                    </div>

                    {/* Grid de cartões de pessoas */}
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                        {filteredProfiles.map(profile => (
                            <div
                                key={profile.id}
                                className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-md transition-shadow cursor-pointer"
                                onClick={() => setSelectedUser(profile)}
                            >
                                <div className="p-6">
                                    <div className="flex items-center mb-4">
                                        <div className="h-16 w-16 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-white text-xl font-bold mr-4">
                                            {profile.name.split(' ').map(n => n[0]).join('')}
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-medium text-gray-900 dark:text-white">{profile.name}</h3>
                                            <p className="text-sm text-gray-600 dark:text-gray-400">{profile.role}</p>
                                        </div>
                                    </div>
                                    <div className="space-y-2 mb-4">
                                        <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                                            <User className="h-4 w-4 mr-2" />
                                            {profile.department}
                                        </div>
                                        <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
                                            <Mail className="h-4 w-4 mr-2" />
                                            {profile.email}
                                        </div>
                                    </div>
                                    <div className="flex justify-between items-center mt-4">
                                        <div className="flex space-x-1">
                                            {profile.evaluationHistory
                                                .filter(e => e.year === '2023')
                                                .map((e, i) => (
                                                    <span key={i}>
                                                        {getScoreBadge(e.score)}
                                                    </span>
                                                ))
                                                .slice(0, 1)}
                                        </div>
                                        <button
                                            className="text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 text-sm font-medium"
                                            onClick={(e) => {
                                                e.stopPropagation()
                                                setSelectedUser(profile)
                                            }}
                                        >
                                            Ver perfil
                                        </button>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Mensagem quando não há resultados */}
                    {filteredProfiles.length === 0 && (
                        <div className="bg-white dark:bg-gray-800 shadow-sm rounded-lg p-8 text-center border border-gray-200 dark:border-gray-700">
                            <div className="mx-auto h-12 w-12 text-gray-400 mb-4">
                                <User className="h-12 w-12" />
                            </div>
                            <h3 className="text-lg font-medium text-gray-900 dark:text-white">Nenhuma pessoa encontrada</h3>
                            <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                                Tente ajustar seus filtros para ver mais resultados.
                            </p>
                        </div>
                    )}
                </>
            ) : (
                <div>
                    {/* Perfil detalhado do usuário - a ser implementado */}
                    <div className="mb-6 flex items-center">
                        <button
                            onClick={() => setSelectedUser(null)}
                            className="mr-4 p-2 text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full"
                        >
                            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                                <path fillRule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clipRule="evenodd" />
                            </svg>
                        </button>
                        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                            Perfil de {selectedUser.name}
                        </h1>
                    </div>

                    <div>
                        <p>
                            Dados detalhados do usuário serão exibidos aqui. Para implementação completa, precisamos importar os componentes
                            de visualização de perfil da página de avaliações ou criar novos componentes dedicados.
                        </p>
                    </div>
                </div>
            )}
        </div>
    )
} 