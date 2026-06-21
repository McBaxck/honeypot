import React from 'react';
import './App.css';
import Loader from "./components/Loader";
import 'react-toastify/dist/ReactToastify.css';
import Honeypot from "./components/Honeypot";
import ChooseHoneypot from "./components/ChooseHoneypot";
import RegisterModal from "./components/RegisterModal";
import {toast, ToastContainer} from "react-toastify";
import ConnectModal from "./components/ConnectModal";
import AlertModal from "./components/AlertModal";
import {addCookie, getCookie, removeCookie} from "./local/cookie";


class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: true,
      currentTab: 0,
      currentHoneypot: null,
      registerModalIsOpen: false,
      signInModalIsOpen: false,
      currentUser: null,
      alertMessage: false
    }
    this.changeTab = this.changeTab.bind(this);
    this.getCurrentTab = this.getCurrentTab.bind(this);
    this.selectHoneypot = this.selectHoneypot.bind(this);
    this.openRegisterModal = this.openRegisterModal.bind(this);
    this.closeRegisterModal = this.closeRegisterModal.bind(this);
    this.openSignInModal = this.openSignInModal.bind(this);
    this.closeSignInModal = this.closeSignInModal.bind(this);
    this.setUser = this.setUser.bind(this);
    this.reload = this.reload.bind(this);
    this.closeAlertModal = this.closeAlertModal.bind(this);
  }

  componentDidMount() {
    let userCookie = getCookie('user')
    if(userCookie){
      this.setState({
        currentUser: userCookie,
        currentHoneypot: userCookie.name
      })
    }


    this.launchTimer()
    window.addEventListener('beforeunload', this.handleUnload);
  }

  componentWillUnmount() {
    window.removeEventListener('beforeunload', (event)=>console.log("AFTER_RELOAD EVENT"));
  }

  handleBeforeUnload = (event) => {
    toast.warn("Don't forget to save your progression", {toastId: "alertWarnToast"})
  }

  handleUnload = (event) => {
    if(!this.state.alertMessage){
      console.log("BEFORE_RELOAD EVENT")
      this.handleBeforeUnload()
      setTimeout(()=>{
        console.log("Get event from window's loading")
        this.setState({
          alertMessage: true
        })
      }, 500)
    } else {
      console.log("AFTER_RELOAD EVENT")

    }

  };

  changeTab(cursor){
    this.setState({currentTab: cursor});
  }

  getCurrentTab(){
    return this.state.currentTab
  }

  selectHoneypot(name){
    this.setState({currentHoneypot: name})
  }

  launchTimer(){
    setTimeout(() => this.setState({loading: false}), 2000);
  }

  openRegisterModal() {
    this.setState({ registerModalIsOpen: true });
  }

  closeRegisterModal() {
    this.setState({ registerModalIsOpen: false });
  }

  closeAlertModal(){
    this.setState({
      alertMessage: false
    })
  }

  openSignInModal() {
    this.setState({ signInModalIsOpen: true });
  }

  closeSignInModal() {
    this.setState({ signInModalIsOpen: false });
  }

  setUser(data){
    this.setState({ currentUser: data });
    toast.dark('Store user information for next connections')
    addCookie('user', data)
  }

  reload(){
    this.setState({
      currentHoneypot: null,
      currentUser: null,
      alertMessage: false
    })
    removeCookie('user')
  }

  render() {
    const {loading} = this.state;
    return (
        <div className="App" style={{borderRadius: '10px'}}>
          <RegisterModal close={this.closeRegisterModal}
                         isOpen={this.state.registerModalIsOpen}
                         selectHP={this.selectHoneypot}/>
          <ConnectModal close={this.closeSignInModal}
                        isOpen={this.state.signInModalIsOpen}
                        selectHP={this.selectHoneypot}
                        setUserInfos={this.setUser}
          />
          {loading ? (
              <Loader/>
          ) : (
              <>
                {this.state.currentHoneypot ? (
                    <Honeypot name={this.state.currentHoneypot}
                              selectHP={this.selectHoneypot}
                              launchTimer={this.launchTimer}
                              user={this.state.currentUser}
                    />
                ) : (
                    <ChooseHoneypot selectHP={this.selectHoneypot}
                                    openRegisterModal={this.openRegisterModal}
                                    openSignInModal={this.openSignInModal}
                    />
                )}

              </>
          )}
          {this.state.alertMessage && (
              <AlertModal
                isOpen={this.state.alertMessage}
                reload={this.reload}
                closeModal={this.closeAlertModal}
              />
          )}
          <ToastContainer
              position="bottom-left"
              hideProgressBar={false}
              newestOnTop={true}
              closeOnClick
              rtl={false}
              pauseOnFocusLoss
              draggable
              pauseOnHover
          />
        </div>
    );
  }
}

export default App;
