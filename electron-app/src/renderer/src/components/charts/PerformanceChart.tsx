import React from 'react';
import {
    Bar,
    BarChart,
    CartesianGrid,
    Legend,
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis
} from 'recharts';

interface DataPoint {
    name: string;
    value: number;
    average?: number;
}

interface PerformanceChartProps {
    data: DataPoint[];
    title: string;
    type?: 'line' | 'bar';
    height?: number;
    colors?: {
        primary: string;
        secondary?: string;
    };
}

export const PerformanceChart: React.FC<PerformanceChartProps> = ({
    data,
    title,
    type = 'line',
    height = 300,
    colors = { primary: '#3b82f6', secondary: '#93c5fd' }
}) => {
    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">{title}</h3>
            <ResponsiveContainer width="100%" height={height}>
                {type === 'line' ? (
                    <LineChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                        <XAxis
                            dataKey="name"
                            stroke="#6b7280"
                            fontSize={12}
                            tickLine={false}
                            axisLine={{ stroke: '#d1d5db' }}
                        />
                        <YAxis
                            stroke="#6b7280"
                            fontSize={12}
                            tickLine={false}
                            axisLine={{ stroke: '#d1d5db' }}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                                border: '1px solid #e5e7eb',
                                borderRadius: '0.375rem',
                                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                                color: '#111827'
                            }}
                        />
                        <Legend />
                        <Line
                            type="monotone"
                            dataKey="value"
                            stroke={colors.primary}
                            activeDot={{ r: 8 }}
                            strokeWidth={2}
                            name="Performance"
                        />
                        {data[0]?.average !== undefined && (
                            <Line
                                type="monotone"
                                dataKey="average"
                                stroke={colors.secondary}
                                strokeDasharray="5 5"
                                strokeWidth={2}
                                name="Average"
                            />
                        )}
                    </LineChart>
                ) : (
                    <BarChart data={data}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.1} />
                        <XAxis
                            dataKey="name"
                            stroke="#6b7280"
                            fontSize={12}
                            tickLine={false}
                            axisLine={{ stroke: '#d1d5db' }}
                        />
                        <YAxis
                            stroke="#6b7280"
                            fontSize={12}
                            tickLine={false}
                            axisLine={{ stroke: '#d1d5db' }}
                        />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                                border: '1px solid #e5e7eb',
                                borderRadius: '0.375rem',
                                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                                color: '#111827'
                            }}
                        />
                        <Legend />
                        <Bar
                            dataKey="value"
                            fill={colors.primary}
                            radius={[4, 4, 0, 0]}
                            name="Performance"
                        />
                        {data[0]?.average !== undefined && (
                            <Bar
                                dataKey="average"
                                fill={colors.secondary}
                                radius={[4, 4, 0, 0]}
                                name="Average"
                            />
                        )}
                    </BarChart>
                )}
            </ResponsiveContainer>
        </div>
    );
}; 