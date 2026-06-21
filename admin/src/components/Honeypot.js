import React from 'react';
import Loader from "./Loader";
import VerticalMenu from "./VerticalMenu";
import Home from "./Home";
import logo from "../holypot_logo.png";
import 'react-toastify/dist/ReactToastify.css';
import Modules from "./Modules";
import GlobalLogs from "./GlobalLogs";
import NetworkGraph from "./NetworkGraph";
import Account from "./Account";
import Firewall from "./Firewall";


class Honeypot extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loading: true,
            currentTab: 0,
            currentHoneypot: null
        }
        this.changeTab = this.changeTab.bind(this);
        this.getCurrentTab = this.getCurrentTab.bind(this);
    }

    changeTab(cursor){
        this.setState({currentTab: cursor});
    }

    getCurrentTab(){
        return this.state.currentTab
    }

    componentDidMount() {
        setTimeout(() => this.setState({loading: false}), 3000);
    }

    render() {
        const {loading} = this.state;
        return (
            <>
                {this.state.loading ? (
                    <Loader/>
                ) : (

                    <div className="container">
                        <div className="holypot">
                            {/* eslint-disable-next-line jsx-a11y/anchor-is-valid */}
                            <a href="">
                                <img src={logo}
                                     id="holypot_logo"
                                     width="100"
                                     height="95"
                                     alt="Logo"
                                     />
                            </a>
                            <div className="infos">
                                <span className="hp-name">
                                    <span className="status-dot"></span>
                                    {!this.props.name ? 'default_name' : this.props.name}
                                </span>
                                <span>Created at 2024-25-02 23:34:53</span>
                            </div>
                        </div>
                        <VerticalMenu changeTab={this.changeTab} getTab={this.getCurrentTab}/>
                        {this.state.currentTab === 0 && (
                            <Home changeTab={this.changeTab}/>
                        )}
                        {this.state.currentTab === 2 && (
                            <Modules/>
                        )}
                        {this.state.currentTab === 1 && (
                            <GlobalLogs/>
                        )}
                        {this.state.currentTab === 3 && (
                            <NetworkGraph/>
                        )}
                        {this.state.currentTab === 4 && (
                            <Firewall/>
                        )}
                        {this.state.currentTab === 5 && (
                            <Account user={this.props.user}/>
                        )}
                    </div>)
                }
            </>
        );
    }
}

export default Honeypot;
