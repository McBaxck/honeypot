import React from 'react';
import './styles/status_modal.scss';
import Modal from "react-modal";
import raspberrypi from '../images/raspberrypi.png';

class StatusModal extends React.Component {

    constructor(props) {
        super(props);
        this.state = {
            isIP4Enabled: false,
            isIP6Enabled: false,
            isHostnameEnabled: false,
            isOSEnabled: false,
            isMemoryEnabled: false,
            status: null,
            configuration: null
        }
        this.changeIP4 = this.changeIP4.bind(this);
        this.changeIP6 = this.changeIP6.bind(this);
        this.changeHostname = this.changeHostname.bind(this);
        this.changeOS = this.changeOS.bind(this);
        this.changeMemory = this.changeMemory.bind(this);
    }

    changeIP4(){
        this.setState({isIP4Enabled: !this.state.isIP4Enabled});
    }

    changeIP6(){
        this.setState({isIP6Enabled: !this.state.isIP6Enabled});
    }

    changeHostname(){
        this.setState({isHostnameEnabled: !this.state.isHostnameEnabled});
    }

    changeOS(){
        this.setState({isOSEnabled: !this.state.isOSEnabled});
    }

    changeMemory(){
        this.setState({isMemoryEnabled: !this.state.isMemoryEnabled});
    }

    render() {
        return (
            <Modal
                isOpen={this.props.isOpen}
                onRequestClose={this.props.close}
                style={customStyles}
                contentLabel="HoneyPot Status Modal"

            >
                <div className="setting-modal-head">
                    <div>
                        <span className="title" style={{marginBottom: "15px"}}>
                            <i className="fa-solid fa-microchip fa-lg" style={{marginRight: "10px"}}></i>
                            Current Status</span><br/>
                        <small><i className="fa-solid fa-circle-info"></i>
                            Display and control remotely your HoneyPot and view all status!</small>
                    </div>
                    <i className="fa-solid fa-xmark fa-lg close" onClick={this.props.close}></i>
                </div>

                    <div className="setting-modal-bodies">
                        {this.props.status ? (<>
                        <img src={raspberrypi} style={{marginLeft: "-20px"}} width="300" height="250" alt=""/>
                        <div className="setting-modal-body">
                            <div className="option">
                                <input type="text"
                                       placeholder={!this.state.isIP4Enabled ? "192.168.1.21" : "???"}
                                       id=""
                                       disabled={!this.state.isIP4Enabled}
                                       value={this.state.status && this.state.status['pub']}
                                />
                                <button onClick={this.changeIP4}>{this.state.isIP4Enabled ?
                                    <i className="fa-solid fa-lock-open"></i> :
                                    <i className="fa-solid fa-lock"></i>}</button>
                            </div>
                            <div className="option">
                                <input type="text"
                                       placeholder={!this.state.isIP6Enabled ? "ffff:ffff:ffff:ffff" : "???"}
                                       id="" disabled={!this.state.isIP6Enabled}
                                       value={this.state.status && this.state.status['lo']}
                                />
                                <button onClick={this.changeIP6}>{this.state.isIP6Enabled ?
                                    <i className="fa-solid fa-lock-open"></i> :
                                    <i className="fa-solid fa-lock"></i>}</button>
                            </div>
                            <div className="option">
                                <input type="text"
                                       placeholder={!this.state.isHostnameEnabled ? "default hostname" : "???"}
                                       id=""
                                       disabled={!this.state.isHostnameEnabled}
                                       value={this.state.status && this.state.status['mac']}
                                />
                                <button onClick={this.changeHostname}>{this.state.isHostnameEnabled ?
                                    <i className="fa-solid fa-lock-open"></i> :
                                    <i className="fa-solid fa-lock"></i>}</button>
                            </div>
                            <div className="option">
                                <input type="text"
                                       placeholder={!this.state.isOSEnabled ? "operating system" : "???"}
                                       id=""
                                       disabled={!this.state.isOSEnabled}
                                       value={this.state.status && this.state.status['os']}
                                />
                                <button onClick={this.changeOS}>{this.state.isOSEnabled ?
                                    <i className="fa-solid fa-lock-open"></i> :
                                    <i className="fa-solid fa-lock"></i>}</button>
                            </div>
                            <div className="option">
                                <input type="text"
                                       placeholder={!this.state.isMemoryEnabled ? "RAM / Memory" : "???"}
                                       id=""
                                       disabled={!this.state.isMemoryEnabled}
                                       value={this.state.status && this.state.status['memory']}
                                />
                                <button onClick={this.changeMemory}>{
                                    this.state.isMemoryEnabled ?
                                        <i className="fa-solid fa-lock-open"></i> :
                                        <i className="fa-solid fa-lock"></i>
                                }</button>
                            </div>
                        </div>
                            </>
                        ) : (
                            <div className="load">
                                <small><i className="fa-solid fa-circle-notch fa-spin" style={{
                                    marginRight: "7px", fontWeight: "800", color: "grey", fontSize: ".8em"}}></i>
                                    Loading device configuration, please wait...
                                </small>
                            </div>

                        )}
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
        height: '400px',
        left: '40%',
        right: 'auto',
        bottom: 'auto',
        marginRight: '-50%',
        transform: 'translate(-50%, -50%)',
        overflow: 'hidden'
    },
};

export default StatusModal