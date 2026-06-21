import React from 'react';
import './styles/account.scss';
import avatar from '../images/avatar.png';
import addUser from '../images/add.png';
import {getAccountData} from "../api/holypot";
import {toast} from "react-toastify";
import {getCookie} from "../local/cookie";


class Account extends React.Component {
    // eslint-disable-next-line no-useless-constructor
    constructor(props) {
        super(props);
        this.state = {
            addNewUser: false,
            user: null
        }
        this.getAccount = this.getAccount.bind(this);
    }

    componentDidMount() {
        this.getAccount();
    }


    getAccount(){
        toast.promise(getAccountData(getCookie('user').user), {
            pending: "Retrieve account records",
            error: "Unable to fetch your account data"
        }, {toastId: "fetchAccountToast"}).then(res=> res.json())
            .then(data=>{
                this.setState({user: data})
            })
            .catch(err=>console.error(err))
    }

    truncateString(str, maxLength) {
        // Vérifie si la longueur de la chaîne est supérieure à maxLength
        if (str.length > maxLength) {
            // Coupe la chaîne pour qu'elle soit maxLength - 2 caractères de long
            // (on soustrait 2 pour tenir compte de la longueur de "…3" qui est ajouté à la fin)
            return str.substring(0, maxLength - 2) + '…';
        }
        // Si la chaîne n'est pas plus longue que maxLength, la retourne telle quelle
        return str;
    }

    render() {
        const {user} = this.state;
        return (
            <>

                <div className="profile" hidden={true} style={{display: "none"}}>
                    <div className="avatar" onFocus={() => this.setState({addNewUser: true})}>
                        <img alt="avatar icon 3d" id="avatar" width="110" height="110" src={avatar}/>
                        <img alt="avatar icon 3d" className={this.state.addNewUser && "move"} id="addUser" width="110"
                             height="110" src={addUser}/>

                    </div>
                    <div className="avatar"></div>
                    <div className="profile-infos">
                        <button>Change my BitPot</button>
                        <br/>
                        <button>Share my profile</button>
                    </div>
                </div>

                <div className="accounts">
                    <div className="setting-modal-footer" style={{marginBottom: "20px"}}>
                        <small>
                            <i className="fa-solid fa-triangle-exclamation" style={{marginRight: "7px"}}></i>
                            It's your first connection ? Don't forget to change your password in the Account Tab,
                            and select Hash Mode, to ensure security layer in the registering mode. For admin account,
                            Hash Mode is already activated!
                        </small>
                    </div>
                    <div className="account">
                        <div className="credential">
                            <label><i className="fa-solid fa-user" style={{marginRight: "8px"}}></i>Created at</label>
                            <span>{user && user.created_at}</span>
                        </div>
                        <div className="credential">
                            <label><i className="fa-solid fa-tablet-button" style={{marginRight: "8px"}}></i>Honeypot Name</label>
                            <span>{user && user.name}</span>
                        </div>
                        <div className="credential">
                            <label><i className="fa-solid fa-key" style={{marginRight: "8px"}}></i>Secret Pass</label>
                            <span>{user && this.truncateString(user.password, 20)}</span>
                        </div>
                        <div className="credential">
                            <label><i className="fa-solid fa-signature" style={{marginRight: "8px"}}></i>Username</label>
                            <span>{user && user.user}</span>
                        </div>
                        <div className="credential">
                            <label><i className="fa-solid fa-asterisk" style={{marginRight: "8px"}}></i>Account
                                Type</label>
                            <span>{user && user.type}</span>
                            <div className="actions">
                                <span>
                                    <div style={{marginBottom: "15px"}}>
                                        <i className="fa-solid fa-bars" style={{marginRight: "8px"}}></i>CONFIGURE MY ACCOUNT
                                    </div>
                                    <hr/>
                                    <button className="action">Request for admin account</button><br/>
                                    <button className="action">Delete my account</button><br/>
                                    <button className="action">Download my private data</button><br/>
                                </span>

                            </div>
                        </div>
                    </div>


                </div>
            </>
        )
    }
}


export default Account