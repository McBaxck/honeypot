import React from 'react';
import './styles/register_modal.scss';
import {registerHP, setHoneypotState, testConnection} from "../api/holypot";
import {toast} from "react-toastify";
import {addCookie} from "../local/cookie";
import Modal from "react-modal";

class RegisterModal extends React.Component {
    // eslint-disable-next-line no-useless-constructor
    constructor(props) {
        super(props);
        this.state = {
            isAPIok: null,
            username: '',
            password: '',
            email: '',
            honeypotName: '',
            honeypotIP: null
        }
        this.verifyAPIStatus = this.verifyAPIStatus.bind(this);
        this.setUsername = this.setUsername.bind(this);
        this.setPassword = this.setPassword.bind(this);
        this.register = this.register.bind(this);
        this.setEmail = this.setEmail.bind(this);
        this.setHoneyPotName = this.setHoneyPotName.bind(this);
    }


    setUsername = (event)=>{
        this.setState({username: event.target.value});
    }

    setEmail = (event)=>{
        this.setState({email: event.target.value});
    }

    setHoneyPotName = (event)=>{
        this.setState({honeypotName: event.target.value});
    }

    setPassword = (event)=>{
        this.setState({password: event.target.value});
    }

    verifyAPIStatus = (event) => {
        this.setState({isAPIok: null, honeypotIP: event.target.value});
        if(this.isValidIPV4(event.target.value)){
            toast.promise(this.addTimeOutToPromise(testConnection(event.target.value), 9000), {
                pending: "Test the connection",
                success: "Succesfully connected to honeypot",
                error: `Unable to connect to ${event.target.value} `,
            }).then(res=>res.json()).then(data=>{
                    this.setState({isAPIok: true});
                }).catch(err=>{
                    this.setState({isAPIok: false});
                })
        } else{
            toast.warn(`${event.target.value} is not a valid IP!`, {toastId: "ipWarn", className: "small-toast",})
        }

    }

    addTimeOutToPromise(promise, timeoutMs) {
        let timeoutHandle;
        const timeoutPromise = new Promise((resolve, reject) => {
            timeoutHandle = setTimeout(() => reject(new Error('Operation timed out')), timeoutMs);
        });

        return Promise.race([promise, timeoutPromise]).then((result) => {
            clearTimeout(timeoutHandle);
            return result;
        }, (error) => {
            clearTimeout(timeoutHandle);
            throw error;
        });
    }

    isValidIPV4(data) {
        const regexIPv4 = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        return regexIPv4.test(data);
    }


    register(){
        let credentials = {
            username: this.state.username,
            password: this.state.password,
            email: this.state.email,
            name: this.state.honeypotName
        }
        if(this.state.username && this.state.password){
            toast.promise(registerHP(credentials), {
                pending: "Create your account...",
                success: `Welcome to HolyPot ${this.state.username}!`,
                error: `Unable to create your honeypot`
            }).then(
                res=>res.json()
            ).then(
                data=>{
                    this.props.close();
                    this.props.selectHP(data.name);
                    this.setState({isAPIok: false});
                    let state = {"run": true, "maintenance": false, "ip": this.state.honeypotIP, "honeypot_id": data['honeypot_id']}
                    toast.promise(setHoneypotState(state), {pending: "Register your honeypot", error: "Unable to register your honeypot"})
                        .catch(err=>console.error(err))
                    addCookie('hid', data['honeypot_id'])
                    addCookie('user', data)
                }
            ).catch(
                err=>console.error(err)
            )
        } else{
            toast.warn("Please set a correct username/password!")
        }

    }


    render() {
        return (
            <Modal
                isOpen={this.props.isOpen}
                onRequestClose={this.props.close}
                style={customStyles}
                contentLabel="Register Account Modal"
            >
                <div className="setting-modal-head">
                    <div>
                        <span className="title">Register to your honeypot</span><br/>
                        <small><i className="fa-solid fa-circle-info"></i>
                            Make sure that an account was created before, default credentials could be found
                            in the documentation</small>
                    </div>
                    <i className="fa-solid fa-xmark fa-lg close" onClick={this.props.close}></i>
                </div>
                <div className="setting-modal-footer" style={{marginBottom: "20px"}}>
                    <small>
                        <i className="fa-solid fa-triangle-exclamation" style={{marginRight: "7px"}}></i>
                        It's your first connection ? Don't forget to change your password in the Account Tab,
                        and select Hash Mode, to ensure security layer in the registering mode. For admin account,
                        Hash Mode is already activated!
                    </small>
                </div>
                <div className="credentials">
                    <div className="credential">
                        <label htmlFor="honeypot_ip">
                            <i className="fa-solid fa-server" style={{marginRight: "8px"}}></i>
                            IP Addr.
                            <small><i className="fa-solid fa-circle-question" style={{marginRight: "5px"}}></i>
                                This username is unique for all accounts connected to your honeypot</small>
                        </label>
                        <input type="text" id="honeypot_ip" onChange={this.verifyAPIStatus}
                               disabled={this.state.isAPIok} placeholder="Enter the honeypot ip4 address"/>
                    </div>
                    <div className="credential">
                        <label htmlFor="honeypot_name">
                            <i className="fa-solid fa-server" style={{marginRight: "8px"}}></i>
                            Hostname
                            <small><i className="fa-solid fa-circle-question" style={{marginRight: "5px"}}></i>
                                This username is unique for all accounts connected to your honeypot</small>
                        </label>
                        <input type="text" id="honeypot_name" placeholder="Choose a name for the device"
                               value={this.state.honeypotName} onChange={this.setHoneyPotName}/>
                    </div>
                    <div className="credential">
                        <label htmlFor="username">
                            <i className="fa-regular fa-address-card" style={{marginRight: "8px"}}></i>
                            Username<br/>
                            <small><i className="fa-solid fa-circle-question" style={{marginRight: "5px"}}></i>
                                This username is unique for all accounts connected to your honeypot</small>
                        </label>
                        <input type="text" id="username" value={this.state.username} onChange={this.setUsername}
                               placeholder="Enter a unique username"/>
                    </div>
                    <div className="credential">
                        <label htmlFor="email">
                            <i className="fa-solid fa-at" style={{marginRight: "8px"}}></i>
                            Email
                            <small><i className="fa-solid fa-circle-question" style={{marginRight: "5px"}}></i>
                                This username is unique for all accounts connected to your honeypot</small>
                        </label>
                        <input type="email" id="email" placeholder="Enter your email address"
                               value={this.state.email} onChange={this.setEmail}/>
                    </div>
                    <div className="credential">
                        <label htmlFor="password">
                            <i className="fa-solid fa-key" style={{marginRight: "8px"}}></i>
                            Password
                            <small><i className="fa-solid fa-circle-question" style={{marginRight: "5px"}}></i>
                                This username is unique for all accounts connected to your honeypot</small>
                        </label>
                        <input type="password" id="password" value={this.state.password} onChange={this.setPassword}
                               placeholder="Set a secure password"/>
                    </div>
                    <button onClick={() => this.register()}>
                        <i className="fa-solid fa-user-plus" style={{marginRight: "8px"}}></i>
                        Sign in to honeypot
                    </button>
                </div>
            </Modal>
        )
    }
}

const customStyles = {
    content: {
        top: '50%',
        width: '600px',
        maxHeight: '85vh',
        overflowY: 'auto',
        border: 'none',
        fontFamily: 'Space Grotesk, sans-serif',
        borderRadius: '16px',
        boxShadow: '0 12px 36px rgba(16, 24, 32, .18)',
        backgroundColor: "#FFFEFE",
        height: 'auto',
        padding: '28px',
        left: '50%',
        right: 'auto',
        bottom: 'auto',
        marginRight: '-50%',
        transform: 'translate(-50%, -50%)',
    },
    overlay: {
        backgroundColor: 'rgba(16, 24, 32, .45)',
        zIndex: 1100,
    },
};

export default RegisterModal
