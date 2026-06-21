import React from 'react';
import './styles/module_modal.scss';
import Switch from "./Slider";
import Modal from "react-modal";
import {toast} from "react-toastify";
import {postModuleConfiguration} from "../api/holypot";

class ModuleModal extends React.Component {
    // eslint-disable-next-line no-useless-constructor
    constructor(props) {
        super(props);
        this.state = {
            credentials: false,
            security: false,
            logs: false,
            accounts: [],
            currentUsername: null,
            currentPassword: null,
            antiSpam: false,
            deepDefense: false,
        }
        this.switchSecurity = this.switchSecurity.bind(this);
        this.switchCredentials = this.switchCredentials.bind(this);
        this.switchLogs = this.switchLogs.bind(this);
        this.setCredentialUsername = this.setCredentialUsername.bind(this);
        this.setCredentialPassword = this.setCredentialPassword.bind(this);
        this.addAccountCredentials = this.addAccountCredentials.bind(this);
        this.sendConfiguration = this.sendConfiguration.bind(this);
        this.switchAntiSpam = this.switchAntiSpam.bind(this);
        this.switchDeepDefense = this.switchDeepDefense.bind(this);
        this.resetVolatileConfiguration = this.resetVolatileConfiguration.bind(this);
    }

    componentDidMount() {
    }

    resetVolatileConfiguration(){
        console.log(`Reset last volatile modifications to ${this.props.moduleName} module...`)
        this.setState({
            credentials: true,
            security: true,
            logs: true,
            accounts: []
        })
        this.props.close()
    }

    switchSecurity(){
        this.setState({security: !this.state.security})
        //toast.dark(`security: ${this.state.security}`)
        console.log('security : ', this.state.security)
    }

    switchCredentials(){
        this.setState({credentials: !this.state.credentials})
        //toast.dark(`credentials: ${this.state.credentials}`)
        console.log('credentials : ', this.state.credentials)
    }

    switchLogs(){
        this.setState({logs: !this.state.logs})
        //toast.dark(`logs: ${this.state.logs}`)
        console.log('logs : ', this.state.logs)
    }

    switchAntiSpam(){
        this.setState({antiSpam: !this.state.antiSpam})
        //toast.dark(`logs: ${this.state.logs}`)
        console.log('anti-spam : ', this.state.antiSpam)
    }

    switchDeepDefense(){
        this.setState({deepDefense: !this.state.deepDefense})
        //toast.dark(`logs: ${this.state.logs}`)
        console.log('deep-defense : ', this.state.deepDefense)
    }

    addAccountCredentials(){
        let account = {
            "username": this.state.currentUsername,
            "password": this.state.currentPassword
        }
        this.setState(prevState => {
            const itemExists = prevState.accounts.some(item => this.objectsAreEqual(item, account));

            if (!itemExists) {
                toast("Adding account OK", {toastId: "accountOK"})
                console.log(`>> Add account ${account} to accounts list!`)
                return {
                    accounts: [...prevState.accounts, account],
                    message: '' // Clear any previous message
                };
            } else {
                toast.error('Account already exists', {toastId: "accountNOK"})
                return { message: 'Item already exists in the list' };
            }
        });

    }

    objectsAreEqual(obj1, obj2) {
        const keys1 = Object.keys(obj1);
        const keys2 = Object.keys(obj2);

        if (keys1.length !== keys2.length) {
            return false;
        }

        for (let key of keys1) {
            if (obj1[key] !== obj2[key]) {
                return false;
            }
        }

        return true;
    }

    setCredentialUsername = event => {
        this.setState({currentUsername: event.target.value})
    }

    setCredentialPassword = event => {
        this.setState({currentPassword: event.target.value})
    }

    sendConfiguration(){
        this.state.accounts.forEach(account=>(
            console.log("Account -> ", account)

        ))
        let configuration = {
            "module_name": this.props.moduleName,
            "module_conf":
                {
                    "accounts": this.state.accounts,
                    "options" : {
                        "credentials": !this.state.credentials,
                        "security": !this.state.security,
                        "logs": !this.state.logs
                    },
                    "protections":{
                        "anti_spam": this.state.antiSpam,
                        "deep_defense": this.state.deepDefense
                    }
            }
        }
        toast.promise(postModuleConfiguration(configuration), {
            pending: "Saving the configuration...",
            success: "Configuration: OK",
            error: "Unable to save the configuration"
        })
            .then(response=>response.json)
            .then(data=>{
                console.log(data)
            })
            .catch(err=>console.error(err))
    }

    render() {
        return (
            <Modal
                isOpen={this.props.isOpen}
                onRequestClose={this.resetVolatileConfiguration}
                style={customStyles}
                contentLabel="Module Modal"
            >
                <div className="setting-modal-head">
                    <div>
                        <span className="title">{this.props.moduleName} Configuration</span><br/>
                        <small><i className="fa-solid fa-circle-info"></i>
                            This configuration is not persistent, please be aware of that!</small>
                    </div>
                    <i className="fa-solid fa-xmark fa-lg close" onClick={this.props.close}></i>
                </div>
                <div className="setting-modal-bodies">
                    <div className="setting-modal-body">
                        <div className="setting">
                            <span><i className="fa-solid fa-signal"
                                     style={{marginRight: "5px", opacity: .3}}></i>Credentials</span>
                            <Switch activate={this.switchCredentials}/>
                        </div>
                        <div className="setting">
                            <span><i className="fa-solid fa-signal"
                                     style={{marginRight: "5px", opacity: .3}}></i>Logs</span>
                            <Switch activate={this.switchLogs}/>
                        </div>
                    </div>
                    <div className="setting-modal-body">
                        <div className="setting">
                                <span><i className="fa-solid fa-shield-halved"
                                         style={{marginRight: "5px", opacity: .6}}></i>Security</span>
                            <Switch activate={this.switchSecurity}/>
                        </div>
                    </div>
                    <div className="setting-modal-body">
                        <input hidden id="actual-btn"/>
                        <label className="import-conf" htmlFor="actual-btn" onClick={()=>this.sendConfiguration()}>
                            <i className="fa-regular fa-circle-down fa-lg"></i><br/>
                            <span>Save the current {this.props.moduleName} configuration.</span>
                        </label>

                    </div>

                </div>
                {this.state.credentials && (
                    <div className="setting-modal-bodies" style={{marginTop: "20px"}}>
                        <div className="protocol-info">
                            <small><h1>Credentials</h1>Please set a correct username and passwords to log into the server<br/>
                            Password is clearly visible to help you save it into your brain (ahah)</small>
                        </div>
                        <div className="setting-modal-body">
                            <div className="setting">
                            <span><i className="fa-solid fa-signal"
                                     style={{marginRight: "5px", opacity: .3}}></i>Username</span>
                                <input type="text" className="" placeholder="" onChange={this.setCredentialUsername}/>
                            </div>
                            <div className="setting">
                            <span><i className="fa-solid fa-signal"
                                     style={{marginRight: "5px", opacity: .3}}></i>Password</span>
                                <input type="text" className="" placeholder="" onChange={this.setCredentialPassword}/>
                            </div>
                            <button onClick={()=>{this.addAccountCredentials()}}>Add to service</button>
                        </div>

                    </div>)}
                {this.state.security && (
                    <div className="setting-modal-bodies" style={{marginTop: "20px"}}>
                        <div className="protocol-info">

                            <small><h1>Security</h1><hr/>
                                When security option is active, you could add a protection layer to
                            the kinds of activities the holypot will log into the current module.
                            You can add an "Anti-Spam" and "Deep Defense" option to increase Holypot
                            robustness for DoS</small>
                        </div>
                        <div className="setting-modal-body">

                            <div className="setting">
                                <span><i className="fa-solid fa-shield-halved"
                                         style={{marginRight: "5px", opacity: .6}}></i>Anti-Spam</span>
                                <Switch activate={this.switchAntiSpam}/>
                            </div>
                            <div className="setting">
                                <span><i className="fa-solid fa-shield-halved"
                                         style={{marginRight: "5px", opacity: .6}}></i>Deep Defense</span><br/>
                                <Switch activate={this.switchDeepDefense}/>
                            </div>
                        </div>

                    </div>)}
                <div className="setting-modal-footer">
                    <small>
                        <i className="fa-solid fa-triangle-exclamation" style={{marginRight: "7px"}}></i>
                        Before activating a module, we highly recommend to test the tool
                        connection by clicking on this link: <a>Test and enable my module</a>
                    </small>
                </div>
            </Modal>
        )
    }
}

const customStyles = {
    content: {
        top: '50%',
        width: '700px',
        border: '2px solid #E7E7E7',
        fontFamily: 'Space Grotesk, sans-serif',
        borderRadius: '1rem',
        backgroundColor: "#FFFEFE",
        height: '380px',
        left: '40%',
        right: 'auto',
        bottom: 'auto',
        marginRight: '-50%',
        transform: 'translate(-50%, -50%)',
        overflowX: 'hidden'
    },
};

export default ModuleModal