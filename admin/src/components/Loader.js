import React from 'react';
import logo from '../holypot_logo.png';
import './styles/loader.scss';

class Loader extends React.Component {
    render() {
        return (
            <div className="loader-container space-grotesk">
                <div className="loader-ring">
                    <img src={logo} className="loader-logo" width="64" height="61" alt="HolyPot"/>
                </div>
                <span>Loading</span>
            </div>
        );
    }
}

export default Loader;
