import React, { PureComponent } from 'react';
import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
} from 'recharts';
import { PieChart, Pie, Cell } from 'recharts';
import { getStats } from "../api/holypot";
import './styles/statcharts.scss';

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#00C49F'];

export default class StatCharts extends PureComponent {
    state = {
        byProtocol: null,
    };

    componentDidMount() {
        getStats()
            .then(response => response.json())
            .then(data => {
                const byProtocol = Object.entries(data.by_protocol || {}).map(([name, value]) => ({name, value}));
                this.setState({byProtocol});
            })
            .catch(err => console.error(err))
    }

    render() {
        const {byProtocol} = this.state;
        if (!byProtocol) {
            return <div className="charts">Chargement des statistiques...</div>;
        }
        return (
            <div className="charts">
                <div className="chart">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={byProtocol} margin={{top: 20, right: 20, bottom: 20, left: 0}}>
                            <CartesianGrid strokeDasharray="3 3"/>
                            <XAxis dataKey="name"/>
                            <YAxis allowDecimals={false}/>
                            <Tooltip/>
                            <Legend/>
                            <Bar dataKey="value" name="Connexions" fill="#8884d8"/>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
                <div className="chart">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie data={byProtocol} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                                {byProtocol.map((entry, index) => (
                                    <Cell key={entry.name} fill={COLORS[index % COLORS.length]}/>
                                ))}
                            </Pie>
                            <Tooltip/>
                            <Legend/>
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>
        );
    }
};
