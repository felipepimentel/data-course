import React from 'react';
import {
    Cell,
    Legend,
    Pie,
    PieChart,
    PolarAngleAxis,
    PolarGrid,
    PolarRadiusAxis,
    Radar,
    RadarChart,
    ResponsiveContainer,
    Tooltip
} from 'recharts';

interface RadarDataPoint {
    subject: string;
    value: number;
    fullMark?: number;
}

interface PieDataPoint {
    name: string;
    value: number;
}

interface ComparisonChartProps {
    title: string;
    type: 'radar' | 'pie';
    data: RadarDataPoint[] | PieDataPoint[];
    height?: number;
    colors?: string[];
}

const DEFAULT_COLORS = ['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ef4444'];

export const ComparisonChart: React.FC<ComparisonChartProps> = ({
    title,
    type,
    data,
    height = 300,
    colors = DEFAULT_COLORS
}) => {
    return (
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">{title}</h3>
            <ResponsiveContainer width="100%" height={height}>
                {type === 'radar' ? (
                    <RadarChart data={data as RadarDataPoint[]}>
                        <PolarGrid stroke="#374151" opacity={0.2} />
                        <PolarAngleAxis
                            dataKey="subject"
                            tick={{ fill: '#6b7280', fontSize: 12 }}
                        />
                        <PolarRadiusAxis
                            angle={30}
                            domain={[0, 'auto']}
                            tick={{ fill: '#6b7280', fontSize: 10 }}
                        />
                        <Radar
                            name="Performance"
                            dataKey="value"
                            stroke={colors[0]}
                            fill={colors[0]}
                            fillOpacity={0.6}
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
                    </RadarChart>
                ) : (
                    <PieChart>
                        <Pie
                            data={data as PieDataPoint[]}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            outerRadius={80}
                            innerRadius={30}
                            fill="#8884d8"
                            dataKey="value"
                            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                        >
                            {(data as PieDataPoint[]).map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                            ))}
                        </Pie>
                        <Tooltip
                            formatter={(value, name, props) => [`${value} (${((value as number) / (data as PieDataPoint[]).reduce((sum, item) => sum + item.value, 0) * 100).toFixed(1)}%)`, name]}
                            contentStyle={{
                                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                                border: '1px solid #e5e7eb',
                                borderRadius: '0.375rem',
                                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                                color: '#111827'
                            }}
                        />
                        <Legend />
                    </PieChart>
                )}
            </ResponsiveContainer>
        </div>
    );
}; 