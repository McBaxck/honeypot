import React from 'react';
import './styles/home.scss';
import Dashboard from "./Dashboard";

class Home extends React.Component {
    render() {
        return (
            <div className="home">
                <Dashboard changeTab={this.props.changeTab}/>
            </div>
        )
    }
}

export default Home
