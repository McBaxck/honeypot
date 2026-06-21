import React from 'react';
import 'react-toastify/dist/ReactToastify.css';
import './styles/choose_honeypot.scss';
import bee from '../images/bee.png';

class ChooseHoneypot extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            loading: true,
            currentTab: 0,
            currentHoneypot: null
        }

    }

    render() {
        return (
            <div className="choose-honeypot">
                <div className="honeypots-list">
                    <ul>
                        <li onClick={() => this.props.selectHP("honeypot-1")}>
                            <div className="honey-title">
                                <span><i className="fa-solid fa-hand-pointer fa-beat fa-xs"
                                         style={{marginRight: "8px"}}></i>
                                    Try as anonymous account
                                </span><br/>
                                <small>To test and explore holypot features and possibilities</small>
                                <div className="actions">
                                    <div className="action">
                                        <span>A virtual simulation</span>
                                    </div>
                                    <div className="action">
                                        <span>No storing online</span>
                                    </div>
                                    <div className="action">
                                        <span>Link to local device</span>
                                    </div>
                                </div>

                            </div>

                        </li>
                        <li className="orange" onClick={this.props.openRegisterModal}>
                            <div className="honey-title">
                                <span><i className="fa-solid fa-add fa-xs"
                                         style={{marginRight: "8px"}}></i>
                                    Register my honeypot
                                </span><br/>
                                <small>Add a network connected honeypot, by getting its iPv4 address</small>
                                <div className="actions">
                                    <div className="action">
                                        <span>Create an admin user</span>
                                    </div>
                                    <div className="action">
                                        <span>Sign in your account</span>
                                    </div>
                                    <div className="action">
                                        <span>3+ account max</span>
                                    </div>
                                </div>

                            </div>
                        </li>
                        <li className="purple" onClick={this.props.openSignInModal}>
                            <div className="honey-title">
                                <span><i className="fa-solid fa-right-to-bracket fa-xs"
                                style={{marginRight: "8px"}}></i>
                                Connect on my honeypot
                                </span><br/>
                                <small>Add a network connected honeypot, by getting its iPv4 address</small>
                                <div className="actions">
                                    <div className="action">
                                        <span>Connect to your user</span>
                                    </div>
                                    <div className="action">
                                        <span>Last progress update</span>
                                    </div>
                                    <div className="action">
                                        <span>Share some config.</span>
                                    </div>
                                </div>

                            </div>
                        </li>
                    </ul>
                </div>
                <div className="illustration">
                    <img src={bee} alt="bee 3d"/>
                </div>
            </div>
        );
    }
}

export default ChooseHoneypot;
