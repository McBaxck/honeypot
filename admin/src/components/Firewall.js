import React from 'react';
import './styles/firewall.scss';
import {blockIp, getBlockedIps, unblockIp} from "../api/holypot";
import {toast} from "react-toastify";

class Firewall extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            blocked: null,
            newIp: '',
            newReason: '',
            searchTerm: ''
        }
        this.refresh = this.refresh.bind(this);
        this.handleBlock = this.handleBlock.bind(this);
        this.handleUnblock = this.handleUnblock.bind(this);
    }

    componentDidMount() {
        this.refresh();
    }

    refresh(){
        getBlockedIps().then(r => r.json()).then(data => {
            this.setState({blocked: data});
        }).catch(err => console.error(err))
    }

    handleBlock(event){
        event.preventDefault();
        if (!this.state.newIp) return;
        toast.promise(blockIp(this.state.newIp, this.state.newReason), {
            pending: 'Blocking IP...',
            success: 'IP blocked',
            error: 'Unable to block IP'
        }).then(() => {
            this.setState({newIp: '', newReason: ''});
            this.refresh();
        }).catch(err => console.error(err))
    }

    handleUnblock(ip){
        toast.promise(unblockIp(ip), {
            pending: 'Unblocking IP...',
            success: 'IP unblocked',
            error: 'Unable to unblock IP'
        }).then(() => this.refresh())
            .catch(err => console.error(err))
    }

    filteredBlocked(){
        const {blocked, searchTerm} = this.state;
        if (!blocked) return [];
        const term = searchTerm.trim().toLowerCase();
        if (!term) return blocked;
        return blocked.filter(row =>
            row.ip?.toLowerCase().includes(term) || row.reason?.toLowerCase().includes(term)
        );
    }

    render() {
        const {blocked} = this.state;
        const filtered = this.filteredBlocked();
        return (
            <div className="firewall">
                <div className="firewall-header">
                    <h2>
                        <i className="fa-solid fa-shield-halved" style={{marginRight: "10px"}}></i>
                        {blocked ? `${blocked.length} IP bloquée${blocked.length === 1 ? '' : 's'}` : 'Pare-feu'}
                    </h2>
                </div>

                <form className="block-form" onSubmit={this.handleBlock}>
                    <input type="text" placeholder="Adresse IP"
                           value={this.state.newIp}
                           onChange={e => this.setState({newIp: e.target.value})}/>
                    <input type="text" placeholder="Raison (optionnel)"
                           value={this.state.newReason}
                           onChange={e => this.setState({newReason: e.target.value})}/>
                    <button type="submit">
                        <i className="fa-solid fa-ban" style={{marginRight: "8px"}}></i>
                        Bloquer
                    </button>
                </form>

                {blocked && blocked.length > 0 && (
                    <div className="firewall-search">
                        <i className="fa-solid fa-magnifying-glass"></i>
                        <input type="text" placeholder="Filtrer par IP ou raison..."
                               value={this.state.searchTerm}
                               onChange={e => this.setState({searchTerm: e.target.value})}/>
                    </div>
                )}

                {blocked ? (
                    <table>
                        <thead>
                        <tr>
                            <th>IP</th>
                            <th>Raison</th>
                            <th>Depuis</th>
                            <th></th>
                        </tr>
                        </thead>
                        <tbody>
                        {filtered.map((row) => (
                            <tr key={row.ip}>
                                <td>{row.ip}</td>
                                <td>{row.reason}</td>
                                <td>{row.created_at}</td>
                                <td>
                                    <button className="unblock" onClick={() => this.handleUnblock(row.ip)}>
                                        Débloquer
                                    </button>
                                </td>
                            </tr>
                        ))}
                        </tbody>
                    </table>
                ) : (
                    <div className="loading">
                        <i className="fa-solid fa-spinner fa-spin" style={{marginRight: "8px"}}></i>
                        <span>Loading blocked IPs...</span>
                    </div>
                )}
            </div>
        )
    }
}

export default Firewall
