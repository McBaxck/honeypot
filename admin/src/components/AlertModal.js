import React from 'react';
import './styles/module_modal.scss';
import Modal from "react-modal";


class ModuleModal extends React.Component {
    // eslint-disable-next-line no-useless-constructor
    constructor(props) {
        super(props);
        this.state = {
        }
    }

    componentDidMount() {
    }

    render() {
        return (
            <Modal
                isOpen={this.props.isOpen}
                onRequestClose={null}
                style={customStyles}
                contentLabel="Module Modal"
            >
                <div className="setting-modal-bodies">
                    <div className="setting-modal-body">
                        <button onClick={() => this.props.reload()}>
                            <i className="fa-solid fa-floppy-disk" style={{marginRight: '8px'}}></i>
                            Yes, save my checkpoint
                        </button>
                        <button onClick={() => this.props.closeModal()}>
                            <i className="fa-regular fa-circle-xmark" style={{marginRight: '8px'}}></i>
                            No, keep me on this page
                        </button>
                    </div>
                </div>
                <div className="setting-modal-footer">
                    <small>
                        <i className="fa-solid fa-triangle-exclamation" style={{marginRight: "7px"}}></i>
                        You're about to quit your HolyPot session, be aware that your current configuration must be saved !
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
        width: '520px',
        border: '2px solid #E7E7E7',
        fontFamily: 'Space Grotesk, sans-serif',
        borderRadius: '1rem',
        backgroundColor: "#FFFEFE",
        height: '160px',
        left: '40%',
        right: 'auto',
        bottom: 'auto',
        marginRight: '-50%',
        transform: 'translate(-50%, -50%)',
        overflowX: 'hidden'
    },
};

export default ModuleModal