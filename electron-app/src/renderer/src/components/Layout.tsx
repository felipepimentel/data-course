import { Bell, ClipboardList, LayoutDashboard, Moon, Search, Settings, Sun, Users } from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

interface LayoutProps {
    children: React.ReactNode
}

export function Layout({ children }: LayoutProps) {
    const location = useLocation()
    const [isDarkMode, setIsDarkMode] = useState(false)
    const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)

    const navigation = [
        { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
        { name: 'Avaliações', href: '/evaluations', icon: ClipboardList },
        { name: 'Pessoas', href: '/people', icon: Users },
        { name: 'Configurações', href: '/settings', icon: Settings },
    ]

    useEffect(() => {
        // Check for saved theme preference or use system preference
        const savedTheme = localStorage.getItem('theme')
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches

        if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
            setIsDarkMode(true)
            document.documentElement.classList.add('dark')
        }
    }, [])

    const toggleDarkMode = () => {
        if (isDarkMode) {
            document.documentElement.classList.remove('dark')
            localStorage.setItem('theme', 'light')
        } else {
            document.documentElement.classList.add('dark')
            localStorage.setItem('theme', 'dark')
        }
        setIsDarkMode(!isDarkMode)
    }

    return (
        <div className="h-screen bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 flex overflow-hidden">
            {/* Sidebar - desktop */}
            <div className="hidden md:flex md:flex-col md:w-64 md:fixed md:inset-y-0 border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-800 z-20">
                <div className="flex flex-col h-full">
                    <div className="flex items-center h-16 flex-shrink-0 px-4 border-b border-gray-200 dark:border-gray-700">
                        <h1 className="text-xl font-bold text-blue-600 dark:text-blue-400">Análise de Desempenho</h1>
                    </div>
                    <div className="flex-1 flex flex-col overflow-y-auto pt-5 pb-4">
                        <nav className="flex-1 px-4 space-y-3">
                            {navigation.map((item) => {
                                const isActive = location.pathname === item.href
                                const Icon = item.icon
                                return (
                                    <Link
                                        key={item.name}
                                        to={item.href}
                                        className={`
                                            group flex items-center px-3 py-2.5 text-sm font-medium rounded-md
                                            ${isActive
                                                ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'
                                                : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700/30'}
                                        `}
                                    >
                                        <Icon className={`
                                            mr-3 h-5 w-5
                                            ${isActive
                                                ? 'text-blue-500 dark:text-blue-400'
                                                : 'text-gray-500 group-hover:text-gray-600 dark:text-gray-400 dark:group-hover:text-gray-300'}
                                        `} />
                                        {item.name}
                                    </Link>
                                )
                            })}
                        </nav>
                    </div>
                </div>
            </div>

            {/* Mobile menu button */}
            <div className="md:hidden fixed top-0 left-0 z-40 w-full bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between h-16 px-4">
                    <button
                        type="button"
                        className="text-gray-500 dark:text-gray-400 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none p-2"
                        onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
                    >
                        <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </button>
                    <h1 className="text-lg font-bold text-blue-600 dark:text-blue-400">Análise de Desempenho</h1>
                    <button
                        type="button"
                        className="text-gray-500 dark:text-gray-400 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none p-2"
                        onClick={toggleDarkMode}
                    >
                        {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
                    </button>
                </div>
            </div>

            {/* Mobile menu overlay */}
            {isMobileMenuOpen && (
                <div className="md:hidden fixed inset-0 z-30 bg-gray-600 bg-opacity-75" onClick={() => setIsMobileMenuOpen(false)}>
                    <div className="fixed inset-y-0 left-0 w-64 bg-white dark:bg-gray-800 transition transform mobile-menu" onClick={(e) => e.stopPropagation()}>
                        <div className="pt-16 pb-3 px-4 space-y-1">
                            {navigation.map((item) => {
                                const isActive = location.pathname === item.href
                                const Icon = item.icon
                                return (
                                    <Link
                                        key={item.name}
                                        to={item.href}
                                        className={`
                                            group flex items-center px-3 py-3 text-sm font-medium rounded-md
                                            ${isActive
                                                ? 'bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400'
                                                : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700/30'}
                                        `}
                                        onClick={() => setIsMobileMenuOpen(false)}
                                    >
                                        <Icon className={`
                                            mr-3 h-5 w-5
                                            ${isActive
                                                ? 'text-blue-500 dark:text-blue-400'
                                                : 'text-gray-500 group-hover:text-gray-600 dark:text-gray-400 dark:group-hover:text-gray-300'}
                                        `} />
                                        {item.name}
                                    </Link>
                                )
                            })}
                        </div>
                    </div>
                </div>
            )}

            {/* Main content */}
            <div className="flex flex-col flex-1 md:pl-64">
                {/* Top header - desktop */}
                <div className="sticky top-0 z-10 md:flex h-16 items-center justify-between px-4 sm:px-6 md:px-8 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                    <div className="flex-1 flex max-w-xs">
                        <div className="relative w-full">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Search className="h-5 w-5 text-gray-400" />
                            </div>
                            <input
                                type="text"
                                placeholder="Buscar..."
                                className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 placeholder-gray-500 dark:placeholder-gray-400 focus:placeholder-gray-400 dark:focus:placeholder-gray-500 focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500 dark:focus:border-blue-400 sm:text-sm"
                            />
                        </div>
                    </div>
                    <div className="ml-4 flex items-center md:ml-6 space-x-2">
                        <button className="p-2 rounded-md text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none">
                            <Bell className="h-5 w-5" />
                        </button>
                        <button className="p-2 rounded-md text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none" onClick={toggleDarkMode}>
                            {isDarkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
                        </button>
                    </div>
                </div>

                {/* Page content */}
                <main className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900 pt-16 md:pt-0">
                    {children}
                </main>
            </div>
        </div>
    )
} 