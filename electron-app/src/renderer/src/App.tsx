import { Navigate, Route, Routes } from 'react-router-dom'
import { Layout } from './components/Layout'
import { DashboardPage } from './pages/DashboardPage'
import { EvaluationsPage } from './pages/EvaluationsPage'
import { PeoplePage } from './pages/PeoplePage'
import { SettingsPage } from './pages/SettingsPage'
import './styles/App.css'

function App(): JSX.Element {
    return (
        <Layout>
            <Routes>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/evaluations" element={<EvaluationsPage />} />
                <Route path="/people" element={<PeoplePage />} />
                <Route path="/settings" element={<SettingsPage />} />
                <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
        </Layout>
    )
}

export default App 