import React from 'react';
import './styles/module_modal.scss';
import Modal from "react-modal";


class DeviceModal extends React.Component {
    // eslint-disable-next-line no-useless-constructor
    constructor(props) {
        super(props);
        this.state = {
            deviceIP: null,
            deviceName: null
        }
        this.setDeviceName = this.setDeviceName.bind(this);
        this.setDeviceIP = this.setDeviceIP.bind(this);
        this.addNewDevice = this.addNewDevice.bind(this);
    }

    componentDidMount() {
    }

    setDeviceIP = (e) => {
        this.setState({
            deviceIP: e.target.value
        })
    }

    setDeviceName = (e) => {
        this.setState({
            deviceName: e.target.value
        })
    }

    addNewDevice(){
        let payload = {
            "data": {
                "id": this.state.deviceIP,
                "label": this.state.deviceName
            }
        }
        this.props.addDevice(payload)
        this.props.closeModal();
    }

    render() {
        return (
            <Modal
                isOpen={this.props.isOpen}
                onRequestClose={null}
                style={customStyles}
                contentLabel="Module Modal"
            >
                <div className="setting-modal-head">
                    <h1>Record devices to network</h1>
                    <img
                        src='https://cdn3d.iconscout.com/3d/premium/thumb/honey-jar-6272714-5175140.png'
                        width='200'
                        style={{borderRadius: ".4rem"}}/>

                </div>

                <div className="setting-modal-bodies">

                    <div className="setting-modal-body">
                        <input type='text' onChange={this.setDeviceIP} placeholder="IPv4 or IPv6 Address"/>
                        <input type='text' onChange={this.setDeviceName} placeholder="Hostname / Common label"/>
                    </div>
                    <div className="setting-modal-body">
                        <button onClick={this.addNewDevice}>
                            <i className="fa-solid fa-floppy-disk" style={{marginRight: '8px'}}></i>
                            Register the device
                        </button>
                    </div>
                </div>
                <div className="setting-modal-footer">
                    <small style={{backgroundColor: 'orange', color: 'white'}}>
                        <i className="fa-solid fa-triangle-exclamation" style={{marginRight: "7px"}}></i>
                        You're about to quit your HolyPot session, be aware that your current configuration must be
                        saved !
                        For more information, please check the documentation on our website.
                    </small>
                </div>
            </Modal>
        )
    }
}

const customStyles = {
    content: {
        top: '50%',
        width: '500px',
        border: '2px solid #E7E7E7',
        fontFamily: 'Space Grotesk, sans-serif',
        borderRadius: '1rem',
        backgroundColor: "#FFFEFE",
        height: '430px',
        left: '40%',
        right: 'auto',
        bottom: 'auto',
        marginRight: '-50%',
        transform: 'translate(-50%, -50%)',
        overflowX: 'hidden'
    },
};

export default DeviceModal