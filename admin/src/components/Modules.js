import React from 'react';
import './styles/modules.scss';
import ModuleModal from "./ModuleModal";

class Modules extends React.Component {
    constructor(props){
        super(props)
        this.state = {
            isModuleModalOpen: false,
            currentModuleSelected: null
        }
        this.openModuleModal = this.openModuleModal.bind(this);
        this.closeModuleModal = this.closeModuleModal.bind(this);
        this.changeModuleName = this.changeModuleName.bind(this);
    }

    openModuleModal(){
        this.setState({ isModuleModalOpen: true });
    }

    closeModuleModal(){
        this.setState({ isModuleModalOpen: false });
    }

    changeModuleName(name){
        this.setState({ currentModuleSelected: name });
    }
    render() {
        return (
            <>
                <ModuleModal close={this.closeModuleModal}
                             isOpen={this.state.isModuleModalOpen}
                             moduleName={this.state.currentModuleSelected}
                />
                <div className="info">
                    <i className="fa-regular fa-circle-question"></i>
                    <span>Modules can be added to your current HoneyPot state to handle some scenarios and attackers categories.
                    Local modules are already downloaded and configure on it, but you have to add it from the left list. Public
                        modules are available for downloading (need Internet connection)
                    </span>
                </div>
                <div className="modules">
                    <div className="local-modules">
                        <div className="module icon-container" onClick={() => {
                            this.setState({currentModuleSelected: 'WIFI'})
                            this.openModuleModal()
                        }}>
                            <div>
                                <i className="fa-solid fa-wifi fa-3x" style={{color: "rgba(14,14,14,0.76)"}}></i><br/>
                                <span className="module-subinfo">
                                    <i className="fa-solid fa-circle-info" style={{marginRight: "6px"}}></i>Simulate a fake wifi access point
                                </span>
                            </div>
                            <small><i className="fa-solid fa-circle fa-fade"
                                      style={{color: "red"}}></i>disable</small>

                        </div>
                        <div className="module icon-container" onClick={() => {
                            this.setState({currentModuleSelected: 'SMTP'})
                            this.openModuleModal()
                        }}>
                            <div>
                                <i className="fa-solid fa-paper-plane fa-3x" style={{color: "rgba(14,14,14,0.76)"}}></i><br/>
                                <span className="module-subinfo">
                                    <i className="fa-solid fa-circle-info" style={{marginRight: "6px"}}></i>Simulate a fake mail server
                                </span>

                            </div>

                            <small><i className="fa-solid fa-circle fa-fade"
                                      style={{color: "red"}}></i>disable</small>
                        </div>
                        <div className="module icon-container" onClick={() => {
                            this.setState({currentModuleSelected: 'FTP'})
                            this.openModuleModal()
                        }}>
                            <div>
                                <i className="fa-regular fa-file fa-3x" style={{color: "rgba(14,14,14,0.76)"}}></i>
                                <span className="module-subinfo">
                                    <i className="fa-solid fa-circle-info" style={{marginRight: "6px"}}></i>Simulate a fake file server
                                </span>
                            </div>

                            <small><i className="fa-solid fa-circle fa-fade"
                                      style={{color: "red"}}></i>disable</small>
                        </div>
                        <div className="module icon-container" onClick={() => {
                            this.setState({currentModuleSelected: 'SSH'})
                            this.openModuleModal()
                        }}>
                            <div>
                                <i className="fa-solid fa-certificate fa-3x" style={{color: "rgba(14,14,14,0.76)"}}></i>
                                <span className="module-subinfo">
                                    <i className="fa-solid fa-circle-info" style={{marginRight: "6px"}}></i>Simulate a secure shell server
                                </span>
                            </div>

                            <small><i className="fa-solid fa-circle fa-fade"
                                      style={{color: "red"}}></i>disable</small>
                        </div>
                        <div className="module icon-container" onClick={() => {
                            this.setState({currentModuleSelected: 'Telnet'})
                            this.openModuleModal()
                        }}>
                            <div>
                                <i className="fa-solid fa-terminal fa-3x" style={{color: "rgba(14,14,14,0.76)"}}></i>

                                <span className="module-subinfo">
                                    <i className="fa-solid fa-circle-info" style={{marginRight: "6px"}}></i>Simulate a telnet server
                                </span>
                            </div>
                            <small><i className="fa-solid fa-circle fa-fade"
                                      style={{color: "red"}}></i>disable</small>
                        </div>
                        <button className="" id="add-module">
                            <i className="fa-solid fa-download fa-lg"></i>
                            Download
                        </button>
                    </div>
                </div>
            </>
        )
    }
}

export default Modules