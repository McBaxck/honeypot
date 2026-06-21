import React from 'react';
import './styles/register_modal.scss';
import Modal from "react-modal";
import {toast} from "react-toastify";
import {signInHP, testConnection, addTimeOutToPromise} from "../api/holypot";
import {addCookie} from "../local/cookie";

class ConnectModal extends React.Component {
    // eslint-disable-next-line no-useless-constructor
    constructor(props) {
        super(props);
        this.state = {
            isAPIok: null,
            username: '',
            password: ''
        }
        this.verifyAPIStatus = this.verifyAPIStatus.bind(this);
        this.setUsername = this.setUsername.bind(this);
        this.setPassword = this.setPassword.bind(this);
    }


    setUsername = (event)=>{
        this.setState({username: event.target.value});
    }

    setPassword = (event)=>{
        this.setState({password: event.target.value});
    }



    verifyAPIStatus = (event) => {
        this.setState({isAPIok: null});
        if(this.isValidIPV4(event.target.value)){
            toast.promise(addTimeOutToPromise(testConnection(event.target.value), 9000), {
                pending: "Test the connection",
                success: "Succesfully connected to honeypot",
                error: `Unable to connect to ${event.target.value} `,
            }, {toastId: "connectToastId"}).then(res=>res.json()).then(data=>{
                this.setState({isAPIok: true});
            }).catch(err=>{
                this.setState({isAPIok: false});
            })
        }
    }


    isValidIPV4(data) {
        const regexIPv4 = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/;
        return regexIPv4.test(data);
    }


    signIn(){
        let credentials = {
            username: this.state.username,
            password: this.state.password
        }
        if(this.state.username && this.state.password){
            toast.promise(signInHP(credentials), {
                pending: "Connecting to your account...",
                error: `Unable to sign in your honeypot`
            }).then(
                res=> {
                    if (res.status === 200){
                        res.json().then(r => {
                            this.props.close();
                            this.props.selectHP(r.name);
                            this.setState({isAPIok: false});
                            this.props.setUserInfos(r);
                            addCookie('hid', r['honeypot_id'])
                        })
                    }
                    else if(res.status >= 400){
                        toast.warn("username/password incorrect!")
                    }
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
                        <span className="title">Connect to your honeypot</span><br/>
                        <small><i className="fa-solid fa-circle-info"></i>
                            Make sure that an account was created before, default credentials could be found
                            in the documentation</small>
                    </div>
                    <i className="fa-solid fa-xmark fa-lg close" onClick={this.props.close}></i>
                </div>
                <div className="credentials">
                    <div className="credential">
                        <label htmlFor="honeypot_ip">
                            <i className="fa-solid fa-server" style={{marginRight: "8px"}}></i>
                            Honeypot
                        </label>
                        <input type="text" id="honeypot_ip" onChange={this.verifyAPIStatus}
                               disabled={this.state.isAPIok} placeholder="192.168.x.x"/>
                    </div>
                    <div className="credential">
                        <label htmlFor="username">
                            <i className="fa-regular fa-address-card" style={{marginRight: "8px"}}></i>
                            Username
                        </label>
                        <input type="text" id="username" value={this.state.username} onChange={this.setUsername}
                               placeholder="Enter your username"/>
                    </div>
                    <div className="credential">
                        <label htmlFor="password">
                            <i className="fa-solid fa-key" style={{marginRight:"8px"}}></i>
                            Password</label>
                        <input type="password" id="password" value={this.state.password} onChange={this.setPassword}
                               placeholder="Enter your password"/>
                    </div>
                    <button onClick={()=>this.signIn()}>
                        <i className="fa-solid fa-right-to-bracket" style={{marginRight: "8px"}}></i>
                        Connect to honeypot
                    </button>
                </div>
            </Modal>
        )
    }
}

const customStyles = {
    content: {
        top: '50%',
        width: '480px',
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

export default ConnectModal
