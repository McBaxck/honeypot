import React from 'react';
import './styles/verticalmenu.scss';

class VerticalMenu extends React.Component {

    constructor(props) {
        super(props);
        this.state = {

        }
    }
    render() {
        return (
            <div className="vertical-menu">
                {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
                <a href="#" className={this.props.getTab() === 0 ? "active" : "disable"} onClick={() => this.props.changeTab(0)}>
                    <i className="fa-solid fa-house"></i>
                    Home
                </a>
                <a href="#" className={this.props.getTab() === 1 ? "active" : "disable"} onClick={() => this.props.changeTab(1)}>
                    <i className="fa-solid fa-chart-line"></i>
                    Activities
                </a>
                <a href="#" className={this.props.getTab() === 2 ? "active" : "disable"} onClick={() => this.props.changeTab(2)}>
                    <i className="fa-solid fa-cubes"></i>
                    Modules
                </a>
                <a href="#" className={this.props.getTab() === 3 ? "active" : "disable"} onClick={() => this.props.changeTab(3)}>
                    <i className="fa-solid fa-circle-nodes"></i>
                    Clusters
                </a>
                <a href="#" className={this.props.getTab() === 4 ? "active" : "disable"} onClick={() => this.props.changeTab(4)}>
                    <i className="fa-solid fa-shield-halved"></i>
                    Firewall
                </a>
                <a href="#" className={this.props.getTab() === 5 ? "active" : "disable"} onClick={() => this.props.changeTab(5)}>
                    <i className="fa-solid fa-circle-user fa-lg"></i>
                    Account
                </a>
                <div className="menu-logo">
                    <span>HolyPot is powered by McBaxck© - v0.1.1 (alpha)</span>
                </div>
            </div>
        );
    }
}

export default VerticalMenu;
