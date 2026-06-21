import React, { Component } from 'react';
import './styles/slider.scss'; // Assurez-vous d'avoir ce fichier CSS pour les styles

class Switch extends Component {
    constructor(props) {
        super(props);
        this.state = {
            type: props.option
        }
    }
    render() {
        return (
            <label className="switch">
                <input type="checkbox" checked={this.props.type && this.props.on(this.state.type)} onChange={()=> {
                        this.props.activate()
                }}/>
                <span className="slider round"></span>
            </label>
        );
    }
}

export default Switch;
