import React from 'react';
import hw from '../images/server_honeypot.png';
import './styles/dashboard.scss';
import {getStats, getStatusInfo, getHolypotGlobalLogs, streamLogsUrl} from "../api/holypot";
import {toast} from "react-toastify";
import StatusModal from "./StatusModal";

const PROTOCOL_ICONS = {
    ssh: 'fa-terminal',
    http: 'fa-globe',
    smtp: 'fa-envelope',
    telnet: 'fa-network-wired',
    ftp: 'fa-folder-open',
};

const MAX_FEED_ROWS = 8;

class Dashboard extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            stats: null,
            statusModalIsOpen: false,
            status: null,
            feed: []
        }
        this.openStatusModal = this.openStatusModal.bind(this);
        this.closeStatusModal = this.closeStatusModal.bind(this);
        this.getHPStatus = this.getHPStatus.bind(this);
        this.goToFirewall = this.goToFirewall.bind(this);
        this.eventSource = null;
    }

    componentDidMount() {
        this.loadStats();
        this.loadInitialFeed();
        this.connectLiveStream();
    }

    componentWillUnmount() {
        if (this.eventSource) {
            this.eventSource.close();
        }
    }

    loadStats(){
        getStats()
            .then(response => response.json())
            .then(data => this.setState({stats: data}))
            .catch(err => console.error(err))
    }

    loadInitialFeed(){
        getHolypotGlobalLogs()
            .then(r => r.json())
            .then(data => this.setState({feed: data.slice(0, MAX_FEED_ROWS)}))
            .catch(err => console.error(err))
    }

    connectLiveStream(){
        this.eventSource = new EventSource(streamLogsUrl());
        this.eventSource.onmessage = (event) => {
            const row = JSON.parse(event.data);
            this.setState((prevState) => ({
                feed: [row, ...prevState.feed].slice(0, MAX_FEED_ROWS)
            }));
        };
    }

    getHPStatus(){
        toast.promise(getStatusInfo(), {
            pending: "Fetching device status",
            error: "Unable to fetch honeypot status",
            success: "Honeypot health is ok"
        }).then(r=>r.json())
            .then(data=>{
                this.setState({status: data})
            })
            .catch(err=>console.error(err))
    }

    openStatusModal(){
        this.setState({status: null, statusModalIsOpen: true});
        this.getHPStatus();
    }

    closeStatusModal(){
        this.setState({statusModalIsOpen: false});
    }

    goToFirewall(){
        if (this.props.changeTab) {
            this.props.changeTab(4);
        }
    }

    topSources(){
        const tally = {};
        this.state.feed.forEach(row => {
            if (!row.source_ip) return;
            tally[row.source_ip] = (tally[row.source_ip] || 0) + 1;
        });
        return Object.entries(tally).sort((a, b) => b[1] - a[1]).slice(0, 5);
    }

    render() {
        const {stats, feed} = this.state;
        const topSources = this.topSources();
        return (
            <div className="dashboard">
                <StatusModal close={this.closeStatusModal} isOpen={this.state.statusModalIsOpen}
                             status={this.state.status}/>
                <div className="dashboard-grid">
                    <div className="dashboard-main">
                        {stats && (
                            <div className="stats-row">
                                <div className="stat-card highlight">
                                    <i className="fa-solid fa-wave-square"></i>
                                    <div>
                                        <span className="stat-value">{stats.total_connections}</span>
                                        <span className="stat-label">Connexions totales</span>
                                    </div>
                                </div>
                                {Object.entries(stats.by_protocol || {}).map(([protocol, count]) => (
                                    <div className="stat-card" key={protocol}>
                                        <i className={`fa-solid ${PROTOCOL_ICONS[protocol] || 'fa-circle-nodes'}`}></i>
                                        <div>
                                            <span className="stat-value">{count}</span>
                                            <span className="stat-label">{protocol}</span>
                                        </div>
                                    </div>
                                ))}
                                <div className="stat-card clickable danger" onClick={this.goToFirewall}
                                     title="Voir le pare-feu">
                                    <i className="fa-solid fa-shield-halved"></i>
                                    <div>
                                        <span className="stat-value">{stats.blocked_ips_count}</span>
                                        <span className="stat-label">IP bloquées</span>
                                    </div>
                                </div>
                            </div>
                        )}

                        <div className="panel">
                            <div className="panel-header">
                                <span>
                                    <i className="fa-solid fa-tower-broadcast" style={{marginRight: "8px"}}></i>
                                    Activité en direct
                                </span>
                            </div>
                            {feed.length > 0 ? (
                                <ul className="live-feed">
                                    {feed.map((row, index) => (
                                        <li key={row.id ?? index}>
                                            <span className="badge purple">{row.protocol}</span>
                                            <span className="ip">{row.source_ip}</span>
                                            <span className="arrow">→</span>
                                            <span className="dest">{row.dest_ip}:{row.dest_port}</span>
                                            <span className="country">{(row.country || '').toLowerCase()}</span>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <div className="empty">En attente d'activité...</div>
                            )}
                        </div>
                    </div>

                    <div className="dashboard-side">
                        <img src={hw} height="180" width="180" alt="holypot 3d illustration"/>
                        <button className="status-button" onClick={this.openStatusModal}>
                            <i className="fa-solid fa-chart-simple" style={{marginRight: "8px"}}></i>
                            Status
                        </button>

                        <div className="panel">
                            <div className="panel-header">
                                <span>
                                    <i className="fa-solid fa-ranking-star" style={{marginRight: "8px"}}></i>
                                    Top sources
                                </span>
                            </div>
                            {topSources.length > 0 ? (
                                <ul className="top-sources">
                                    {topSources.map(([ip, count]) => (
                                        <li key={ip}>
                                            <span className="ip">{ip}</span>
                                            <span className="count">{count}</span>
                                        </li>
                                    ))}
                                </ul>
                            ) : (
                                <div className="empty">Pas encore de données</div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}

export default Dashboard;
