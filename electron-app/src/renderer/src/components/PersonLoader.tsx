import { FileJson, Folder, Search } from 'lucide-react';
import React, { useState } from 'react';
import { Alert, Button, Input } from './ui';

interface PersonLoaderProps {
    onPersonsLoaded: (persons: any[]) => void;
}

export const PersonLoader: React.FC<PersonLoaderProps> = ({ onPersonsLoaded }) => {
    const [dataPath, setDataPath] = useState<string>('');
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const handleSelectFolder = async () => {
        try {
            // Use Electron's dialog to select a folder
            const { dialog } = window.require('electron');
            const result = await dialog.showOpenDialog({
                properties: ['openDirectory']
            });

            if (!result.canceled && result.filePaths.length > 0) {
                setDataPath(result.filePaths[0]);
                setError(null);
            }
        } catch (err) {
            setError('Erro ao selecionar pasta: ' + (err as Error).message);
        }
    };

    const loadPersonsData = async () => {
        if (!dataPath) {
            setError('Selecione uma pasta de dados primeiro');
            return;
        }

        setIsLoading(true);
        setError(null);
        setSuccess(null);

        try {
            const { fs, path } = window.require('fs-extra');

            // Find all perfil.json files recursively following the structure <person>/<year>/perfil.json
            const personData: any[] = [];
            const processedPaths = new Set<string>();

            // Function to recursively scan directories
            const scanDirectory = async (dirPath: string) => {
                // Get all entries in the directory
                const entries = await fs.readdir(dirPath, { withFileTypes: true });

                for (const entry of entries) {
                    // Skip hidden files
                    if (entry.name.startsWith('.')) continue;

                    const fullPath = path.join(dirPath, entry.name);

                    if (entry.isDirectory()) {
                        // Check if this directory contains perfil.json and resultado.json
                        const perfilPath = path.join(fullPath, 'perfil.json');
                        const resultadoPath = path.join(fullPath, 'resultado.json');

                        const hasPerfilFile = await fs.pathExists(perfilPath);
                        const hasResultadoFile = await fs.pathExists(resultadoPath);

                        if (hasPerfilFile || hasResultadoFile) {
                            // This is a data directory with at least one of the required files
                            try {
                                const personInfo: any = {
                                    path: fullPath,
                                    name: path.basename(path.dirname(fullPath)),
                                    year: path.basename(fullPath),
                                };

                                // Load profile data if exists
                                if (hasPerfilFile && !processedPaths.has(perfilPath)) {
                                    processedPaths.add(perfilPath);
                                    const perfilData = await fs.readJson(perfilPath);
                                    personInfo.profile = perfilData;
                                }

                                // Load result data if exists
                                if (hasResultadoFile && !processedPaths.has(resultadoPath)) {
                                    processedPaths.add(resultadoPath);
                                    const resultadoData = await fs.readJson(resultadoPath);
                                    personInfo.results = resultadoData;
                                }

                                personData.push(personInfo);
                            } catch (err) {
                                console.error(`Error reading files in ${fullPath}:`, err);
                            }
                        } else {
                            // Recursively scan subdirectories
                            await scanDirectory(fullPath);
                        }
                    }
                }
            };

            // Start scanning from the selected directory
            await scanDirectory(dataPath);

            // Notify parent component about loaded persons
            if (personData.length > 0) {
                onPersonsLoaded(personData);
                setSuccess(`Carregados dados de ${personData.length} pessoas`);
            } else {
                setError('Nenhum dado encontrado na estrutura <pessoa>/<ano>/perfil.json ou resultado.json');
            }
        } catch (err) {
            setError('Erro ao carregar dados: ' + (err as Error).message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 mb-6">
            <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Carregar Dados de Pessoas</h2>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div className="col-span-2">
                    <Input
                        value={dataPath}
                        onChange={(e) => setDataPath(e.target.value)}
                        placeholder="Caminho para pasta de dados"
                        disabled={isLoading}
                    />
                </div>
                <div className="flex space-x-2">
                    <Button onClick={handleSelectFolder} disabled={isLoading} variant="outline">
                        <Folder className="h-4 w-4 mr-2" />
                        Selecionar
                    </Button>
                    <Button onClick={loadPersonsData} disabled={isLoading || !dataPath}>
                        <Search className="h-4 w-4 mr-2" />
                        {isLoading ? 'Carregando...' : 'Carregar'}
                    </Button>
                </div>
            </div>

            {error && (
                <Alert variant="destructive" className="mb-4">
                    {error}
                </Alert>
            )}

            {success && (
                <Alert variant="success" className="mb-4">
                    <FileJson className="h-4 w-4 mr-2" />
                    {success}
                </Alert>
            )}

            <div className="text-sm text-gray-600 dark:text-gray-400">
                <p>O sistema irá procurar por arquivos seguindo a estrutura:</p>
                <pre className="bg-gray-100 dark:bg-gray-900 p-2 rounded mt-1 overflow-auto text-xs">
                    pasta-selecionada/
                    ├── NomePessoa/
                    │   └── Ano/
                    │       ├── perfil.json
                    │       └── resultado.json
                    ├── OutraPessoa/
                    │   └── Ano/
                    │       ├── perfil.json
                    │       └── resultado.json
                </pre>
            </div>
        </div>
    );
}; 