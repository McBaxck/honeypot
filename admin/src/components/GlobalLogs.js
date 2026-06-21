import React from 'react';
import './styles/global_logs.scss';
import {
    getHolypotGlobalLogs, getSrvLogs, streamLogsUrl,
    getSshLogs, getHttpLogs, getTelnetLogs, getFtpLogs
} from "../api/holypot";
import {toast} from "react-toastify";
import elastic_logo from '../images/elastic_search.png';
import StatCharts from "./StatCharts";

const MAX_LIVE_ROWS = 200;

const PROTOCOL_TABS = [
    {id: 1, label: 'SSH', icon: 'fa-terminal', fetch: getSshLogs, columns: ['id', 'created_at', 'source_ip', 'source_port', 'command']},
    {id: 2, label: 'HTTP', icon: 'fa-globe', fetch: getHttpLogs, columns: ['id', 'created_at', 'source_ip', 'source_port', 'user_agent', 'url']},
    {id: 3, label: 'Telnet', icon: 'fa-network-wired', fetch: getTelnetLogs, columns: ['id', 'created_at', 'source_ip', 'source_port', 'command']},
    {id: 4, label: 'FTP', icon: 'fa-folder-open', fetch: getFtpLogs, columns: ['id', 'created_at', 'source_ip', 'event', 'username', 'filename']},
]

class GlobalLogs extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            logs: null,
            currentTab: 0,
            pathLogsHandler: ['system/', 'logs/'],
            currentService: null,
            logsFile: null,
            protocolLogs: {},
            searchTerm: ''
        }
        this.getAllLogs = this.getAllLogs.bind(this);
        this.changeTab = this.changeTab.bind(this);
        this.retrieveServiceLogsFile = this.retrieveServiceLogsFile.bind(this);
        this.eventSource = null;
    }

    componentDidMount() {
        this.getAllLogs();
        this.connectLiveStream();
    }

    componentWillUnmount() {
        if (this.eventSource) {
            this.eventSource.close();
        }
    }

    connectLiveStream() {
        this.eventSource = new EventSource(streamLogsUrl());
        this.eventSource.onmessage = (event) => {
            const row = JSON.parse(event.data);
            this.setState((prevState) => ({
                logs: [row, ...(prevState.logs || [])].slice(0, MAX_LIVE_ROWS)
            }));
        };
    }

    goToPath = (pathName) => {
        if (!this.state.pathLogsHandler.includes(pathName)){
            this.setState((prevState) => ({
                pathLogsHandler: [...prevState.pathLogsHandler, pathName]
            }));
        }

    }

    backToPath = (pathName) => {
        this.setState((prevState) => ({
            pathLogsHandler: prevState.pathLogsHandler.slice(0, prevState.pathLogsHandler.indexOf(pathName)+1)
        }));
    }


    retrieveServiceLogsFile(service){
        getSrvLogs(service).then(res=>res.json()).then(
            success=>{
                //toast.success("Found: logs file!")
                this.setState({logsFile: success, currentService: service});
            }
        ).catch(
            error=>{
                toast.error(error.toString())
                console.error(error)
            }
        )
    }

    changeTab(id){
        this.setState({currentTab: id});
        const protocolTab = PROTOCOL_TABS.find(t => t.id === id);
        if (protocolTab && !this.state.protocolLogs[id]) {
            protocolTab.fetch().then(r => r.json()).then(data => {
                this.setState((prevState) => ({
                    protocolLogs: {...prevState.protocolLogs, [id]: data}
                }));
            }).catch(err => console.error(err));
        }
    }

    getAllLogs(){
        getHolypotGlobalLogs().then(response=>response.json()).then(
            success=>{
                this.setState({logs: success})
            }
        ).catch(err=>{
            console.error(err)
            toast.error(err)
        })
    }

    dateFormater(dateISO) {
        // Création d'un objet Date à partir de la chaîne ISO
        const date = new Date(dateISO);

        // Options pour formater la date
        const options = {
            year: 'numeric', month: 'numeric', day: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit',
            timeZoneName: 'short'
        };

        // Retourne la date formatée selon les options et la locale fr-FR
        return date.toLocaleDateString('fr-FR', options)
    }

    filterBySearch(rows){
        const term = this.state.searchTerm.trim();
        if (!term) return rows;
        return rows.filter(row => Object.values(row).some(
            value => value != null && String(value).toLowerCase().includes(term.toLowerCase())
        ));
    }

    renderSearchBar(){
        return (
            <div className="logs-search">
                <i className="fa-solid fa-magnifying-glass"></i>
                <input type="text" placeholder="Filtrer par IP, pays, commande..."
                       value={this.state.searchTerm}
                       onChange={e => this.setState({searchTerm: e.target.value})}/>
                {this.state.searchTerm && (
                    <button onClick={() => this.setState({searchTerm: ''})}>
                        <i className="fa-solid fa-xmark"></i>
                    </button>
                )}
            </div>
        )
    }

    renderProtocolTable(tab){
        const rows = this.state.protocolLogs[tab.id];
        if (!rows) {
            return (
                <div className="loading">
                    <i className="fa-solid fa-spinner fa-spin" style={{marginRight: "8px"}}></i>
                    <span>loading {tab.label} logs...</span>
                </div>
            )
        }
        const filtered = this.filterBySearch(rows);
        return (
            <>
                {this.renderSearchBar()}
                <table className="logs">
                    <thead>
                    <tr>
                        {tab.columns.map(col => <th key={col}>{col}</th>)}
                    </tr>
                    </thead>
                    <tbody>
                    {filtered.map((row, index) => (
                        <tr key={index}>
                            {tab.columns.map(col => (
                                <td key={col}>{col === 'created_at' ? this.dateFormater(row[col]) : row[col]}</td>
                            ))}
                        </tr>
                    ))}
                    </tbody>
                </table>
            </>
        )
    }

    render() {
        const lastTabId = PROTOCOL_TABS.length; // ids des onglets protocole : 1..PROTOCOL_TABS.length
        return (
            <div className="global-logs">
                <div className="tabs">
                    <div className={this.state.currentTab === 0 ? "tab active" : "tab"}
                         onClick={() => this.changeTab(0)}>
                        <i className="fa-solid fa-chart-simple"></i>
                        <span>Global</span>
                    </div>
                    {PROTOCOL_TABS.map(tab => (
                        <div key={tab.id} className={this.state.currentTab === tab.id ? "tab active" : "tab"}
                             onClick={() => this.changeTab(tab.id)}>
                            <i className={`fa-solid ${tab.icon}`}></i>
                            <span>{tab.label}</span>
                        </div>
                    ))}
                    <div className={this.state.currentTab === lastTabId+1 ? "tab active" : "tab"}
                         onClick={() => this.changeTab(lastTabId+1)}>
                        <i className="fa-solid fa-percent"></i>
                        <span>Repartition</span>
                    </div>
                    <div className={this.state.currentTab === lastTabId+2 ? "tab active" : "tab"}
                         onClick={() => this.changeTab(lastTabId+2)}>
                        <i className="fa-solid fa-floppy-disk"></i>
                        <span>Local</span>
                    </div>
                    <div className={this.state.currentTab === lastTabId+3 ? "tab active" : "tab"}
                         onClick={() => this.changeTab(lastTabId+3)}>
                        <i className="fa-solid fa-cloud"></i>
                        <span>Cloud</span>
                    </div>
                </div>
                {this.state.currentTab === 0 && (
                    this.state.logs ? (
                        <>
                            {this.renderSearchBar()}
                            <table className="logs">
                                <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Date</th>
                                    <th>Source</th>
                                    <th>Destination</th>
                                    <th>Mode</th>
                                    <th>Protocol</th>
                                    <th>Location</th>
                                </tr>
                                </thead>
                                <tbody>
                                {this.filterBySearch(this.state.logs).map((el, index) => (
                                    <tr key={el.id ?? index}>
                                        <td>{el.id}</td>
                                        <td>{this.dateFormater(el.created_at)}</td>
                                        <td>{el.source_ip}</td>
                                        <td>{el.dest_ip}:{el.dest_port}</td>
                                        <td><span className="badge">{el.type}</span></td>
                                        <td><span className="badge purple">{el.protocol}</span></td>
                                        <td><span className="badge pink">{(el.country || '').toLowerCase()}</span></td>
                                    </tr>
                                ))}
                                </tbody>
                            </table>
                        </>
                    ) : (
                        <div className="loading">
                            <i className="fa-solid fa-spinner fa-spin" style={{marginRight: "8px"}}></i>
                            <span>loading activities from device...</span>
                        </div>
                    )
                )}
                {PROTOCOL_TABS.map(tab => this.state.currentTab === tab.id && (
                    <React.Fragment key={tab.id}>{this.renderProtocolTable(tab)}</React.Fragment>
                ))}
                {this.state.currentTab === lastTabId+1 && (
                    <StatCharts/>
                )}
                {this.state.currentTab === lastTabId+2 && (
                    <>
                        <div className="path-saver">
                            {this.state.pathLogsHandler.map((el, index) => (
                                <span className={index === 0 ? "badge blue unauthorized" : "badge blue"} onClick={()=>{
                                    if(this.state.pathLogsHandler.slice(0,2).includes(el)){
                                        this.setState({logsFile: null});
                                        this.backToPath(el);
                                    }
                                }} key={index}>{el}</span>
                            ))}
                        </div>
                        <div className="files">
                            <span className="title"><i className="fa-solid fa-folder-tree" style={{marginRight: "8px"}}></i>
                                Files Tree Stack</span>
                            {this.state.logsFile ? this.state.logsFile.map((logfile, index) => (
                                <div className="file inactive" key={index}>
                                    <div className="name">
                                        <i className="fa-solid fa-file"></i>
                                        <span>{Object.keys(logfile)[0]}</span>
                                    </div>
                                    <div className="export-logfile">
                                        <button>
                                            <i className="fa-solid fa-download" style={{marginRight: "8px"}}></i>
                                            Export
                                        </button>
                                    </div>
                                </div>
                            )) : (
                                <>
                                    <div className="file" onClick={() => {
                                        this.goToPath('ssh/');
                                        this.retrieveServiceLogsFile('ssh');
                                    }}>
                                        <div className="name">
                                            <i className="fa-solid fa-folder"></i>
                                            <span>ssh/</span>
                                        </div>
                                    </div>
                                    <div className="file" onClick={() => {
                                        this.goToPath('smtp/');
                                        this.retrieveServiceLogsFile('smtp');
                                    }}>
                                        <div className="name">
                                            <i className="fa-solid fa-folder"></i>
                                            <span>smtp/</span>
                                        </div>
                                    </div>
                                    <div className="file" onClick={() => {
                                        this.goToPath('ftp/');
                                        this.retrieveServiceLogsFile('ftp');
                                    }}>
                                        <div className="name">
                                            <i className="fa-solid fa-folder"></i>
                                            <span>ftp/</span>
                                        </div>
                                    </div>
                                    <div className="file" onClick={() => {
                                        this.goToPath('telnet/');
                                        this.retrieveServiceLogsFile('telnet');
                                    }}>
                                        <div className="name">
                                            <i className="fa-solid fa-folder"></i>
                                            <span>telnet/</span>
                                        </div>
                                    </div>
                                </>
                            )}


                        </div>
                    </>
                )}
                {this.state.currentTab === lastTabId+3 && (
                    // Cloud platforms...
                    <div className="elastic-search">
                        <img alt="elastic_search_logo" src={elastic_logo} width="80" height="80"/>
                    </div>
                )}
            </div>
        )
    }
}

export default GlobalLogs
